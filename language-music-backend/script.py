import json
import os.path
import re
from typing import Optional, List

import spacy
import torch
import typer
from structlog import get_logger
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer
from typing_extensions import Annotated

from src import firestore
from src.cefr import CEFRIndex
from src.genius import get_song_url, get_lyrics
from src.players import spotify, youtube
from src.players.utils import convert_id
from src.processing import SongProcessor
from src.schemas.song import SongWithLanguage
from src.sound.process import process as transcribe_song
from src.sound.utils import TRANSCRIPTION_FILE_NAME
from src.sync import (
    search_for_segment,
    read_toy_lyrics_data,
    extract_known_passages,
    print_sync_stats_debug,
    clean_lyrics,
    sync_words,
    lrc,
)
from src.wiktionary import WiktionaryScraper

logger = get_logger()
app = typer.Typer()


def __sync_lyrics_for_song(song: SongWithLanguage) -> str:
    """
    Uses fuzzy matching to map between the Whisper Output and the actual scraped lyrics.

    :param song:
    :return: the synced lyrics
    """
    transcription_path = os.path.join(
        "data/songs", song.youtube_id, TRANSCRIPTION_FILE_NAME
    )
    if not os.path.exists(transcription_path):
        raise RuntimeError("Extract transcript first")

    with open(
        os.path.join(f"data/songs/", song.youtube_id, TRANSCRIPTION_FILE_NAME), "r"
    ) as f:
        data = json.load(f)

    lyrics_continuous = clean_lyrics(song.lyrics)
    lyrics_with_new_lines = clean_lyrics(song.lyrics, keep_new_lines=True)

    relevant_segments = data["segments"]
    known_passages = extract_known_passages(relevant_segments, lyrics_continuous)
    synced_words = sync_words(known_passages, data["segments"], lyrics_continuous)

    formatted_lrc = lrc.apply_formatting(lyrics_with_new_lines, synced_words)

    with open(os.path.join(f"data/songs/", song.youtube_id, "lyrics.lrc"), "w") as f:
        f.write(formatted_lrc)

    return formatted_lrc


@app.command()
def read_dictionary_file(dictionary_file: str):
    print("Reading dictionary file...")
    with open(f"data/dictionaries/{dictionary_file}", "r", encoding="latin-1") as f:
        words = f.read().splitlines()

    print(words[:10])


@app.command()
def publish_processed_song(firestore_id: str):
    print("Publishing processed song...")
    db = firestore.init_firestore()

    song: SongWithLanguage = SongWithLanguage(
        **db.collection("songs").document(firestore_id).get().to_dict()
    )
    processor = (
        SongProcessor(song)
        .create_line_reordering_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .mask_words_according_to_tasks()
    )

    processed_song = processor.get_processed_song()

    db.collection("songs").document(firestore_id).set(processed_song.model_dump())


@app.command()
def get_youtube_id(spotify_id: str):
    spotify_client = spotify.SpotifyClient()
    extended_title = spotify_client.fetch_song_extended_title(spotify_id)

    print("Searching youtube for song:" + extended_title)
    youtube_client = youtube.YoutubeClient()
    youtube_id = youtube_client.search_for_song(extended_title)

    print(youtube_id)


@app.command()
def update_with_youtube_id(firestore_id: str):
    db = firestore.init_firestore()

    song: SongWithLanguage = SongWithLanguage(
        **db.collection("songs").document(firestore_id).get().to_dict()
    )
    youtube_id = convert_id(
        source=spotify.SpotifyClient(),
        destination=youtube.YoutubeClient(),
        song_id=song.spotify_id,
    )

    db.collection("songs").document(firestore_id).update({"youtube_id": youtube_id})


def __load_song(title: str, language: str) -> SongWithLanguage:
    spotify_client = spotify.SpotifyClient()
    youtube_client = youtube.YoutubeClient()

    logger.info("Searching for song", title=title)
    spotify_id = spotify_client.search_for_song(title)
    youtube_id = youtube_client.search_for_song(title)

    logger.info("Searching for lyrics")
    genius_url = get_song_url(title)
    lyrics = get_lyrics(genius_url)

    logger.info("Saving song")
    return SongWithLanguage(
        spotify_id=spotify_id,
        youtube_id=youtube_id,
        lyrics=lyrics,
        language=language,
        lyrics_url=genius_url,
    )


@app.command()
def insert_song(title: str, language: str):
    song = __load_song(title, language)

    json.dump(
        song.model_dump(), open(f"data/songs/last_song.json", "w", encoding="utf-8")
    )

    processor = SongProcessor(song)

    processed_song = (
        processor.create_line_reordering_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .mask_words_according_to_tasks()
        .get_processed_song()
    )
    spotify_id = processed_song.spotify_id

    db = firestore.init_firestore()

    db.collection("songs").document(f"spotify-{spotify_id}").set(
        processed_song.model_dump()
    )


@app.command()
def process_locally(title: str, language: str):
    song = __load_song(title, language)
    song_dir = os.path.join("data", "songs", song.youtube_id)
    if not os.path.exists(song_dir):
        os.makedirs(song_dir)

    with open(os.path.join(song_dir, "doc.json"), "w", encoding="utf-8") as f:
        json.dump(song.model_dump(), f, ensure_ascii=False, indent=4)

    if not os.path.exists(os.path.join("data", "songs", song.youtube_id, "lyrics.lrc")):
        transcribe_song(song.youtube_id, language)
        formatted_lrc = __sync_lyrics_for_song(song)
    else:
        with open(os.path.join(song_dir, "lyrics.lrc"), "r", encoding="utf-8") as f:
            formatted_lrc = f.read()

    song.lyrics = formatted_lrc

    processor = SongProcessor(song, keep_lrc=True)

    processed_song = (
        processor.create_line_reordering_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .mask_words_according_to_tasks()
        .get_processed_song()
    )

    with open(os.path.join(song_dir, "processed.json"), "w", encoding="utf-8") as f:
        json.dump(processed_song.model_dump(), f, ensure_ascii=False, indent=4)


@app.command()
def find_one_segment(index: int, start: int):
    data, lyrics = read_toy_lyrics_data()

    first_segment = data["segments"][index]

    longest_passage = search_for_segment(lyrics, first_segment["text"], start=start)

    print(longest_passage)
    print(" ".join(lyrics.split()[longest_passage[0] : longest_passage[1]]))
    print(first_segment["text"])


@app.command()
def find_all_relevant_segments():
    data, lyrics = read_toy_lyrics_data()

    relevant_segments = data["segments"]
    known_passages = extract_known_passages(relevant_segments, lyrics)

    print_sync_stats_debug(known_passages, relevant_segments, lyrics)


@app.command()
def separate_vocals(youtube_id: str, language: str):
    transcribe_song(youtube_id, language)


@app.command()
def sync_lyrics(song_id: str):
    db = firestore.init_firestore()
    song_doc = db.collection("songs").document(song_id).get()
    if not song_doc.exists:
        raise ValueError("Song does not exist")
    song = SongWithLanguage(**song_doc.to_dict())

    __sync_lyrics_for_song(song)


@app.command()
def get_word_details(
    word: str, language: Annotated[Optional[str], typer.Argument()] = "sv"
):
    wiktionary_scraper = WiktionaryScraper(language)
    word_dict = wiktionary_scraper.scrape(word)

    print(json.dumps(word_dict, indent=4))


def __get_clean_lyrics(youtube_id: str) -> str:
    song_dir = os.path.join("data", "songs", youtube_id)
    if os.path.exists(song_dir) and os.path.exists(
        os.path.join(song_dir, "lyrics.lrc")
    ):
        with open(os.path.join(song_dir, "lyrics.lrc"), "r", encoding="utf-8") as f:
            lyrics = f.read()
    else:
        raise Exception("Lyrics not found")

    return re.sub("\[\d+:\d+\.\d+]", "", lyrics)


def __build_vocabulary(words_unique: List[str], song_dir: str):
    wiktionary_scraper = (
        WiktionaryScraper()
    )  # Assumes the lyrics are in Swedish for now
    word_details = {}
    bases = []

    cefr_index = CEFRIndex()
    for word in tqdm(words_unique):
        word_dict = wiktionary_scraper.scrape(word)

        word_details[word] = word_dict
        if word_dict.get("base", None):
            bases.append(word_dict["base"])

    for word in tqdm(bases):
        if word in word_details:
            continue

        base_dict = wiktionary_scraper.scrape(word)
        word_details[word] = base_dict

    word_details_with_level = {}
    for word, word_dict in word_details.items():
        if word_dict.get("base", None):
            continue  # Most probably the derivatives will not be in the list but we will be looking for the base

        cefr_word_data = cefr_index.get_entry(word)
        if cefr_word_data:
            word_dict = {**word_dict, **cefr_word_data.model_dump()}
        else:
            word_dict = {**word_dict, "cefr": "unknown"}
            logger.warn("Couldn't find word in CEFR index", word=word)
        word_details_with_level[word] = word_dict

    with open(os.path.join(song_dir, "vocabulary.json"), "w", encoding="utf-8") as f:
        json.dump(word_details_with_level, f, ensure_ascii=False, indent=4)


@app.command()
def create_song_vocabulary(youtube_id: str):
    lyrics = __get_clean_lyrics(youtube_id)
    song_dir = os.path.join("data", "songs", youtube_id)

    words = lyrics.split()

    words_clean = [re.sub("[,.!?:;]", "", word) for word in words]
    words_unique = list(set(words_clean))

    __build_vocabulary(words_unique, song_dir)


@app.command()
def analyze_with_spacy(youtube_id: str):
    lyrics = __get_clean_lyrics(youtube_id)
    nlp = spacy.load("sv_core_news_lg")
    doc = nlp(lyrics)

    words = [
        (token.text.lower(), token.pos_)
        for token in doc
        if token.pos_ not in ["PUNCT", "SPACE", "PROPN"]
    ]
    words_unique = list(set(words))
    print("Unique words", len(words_unique))
    print("Total words", len(words))
    print(words_unique)

    # __build_vocabulary(words_unique, song_dir=os.path.join("data", "songs", youtube_id))


@app.command()
def analyze_with_transformers(youtube_id: str):
    lyrics = __get_clean_lyrics(youtube_id)
    # Use a pipeline as a high-level helper
    from transformers import pipeline

    pipe = pipeline("token-classification", model="KBLab/bert-base-swedish-cased-pos")

    bert_output = pipe(lyrics)

    print(bert_output)


@app.command()
def extract_definition_with_context(word: str, context: str):
    """
    TODO: this doesn't account for word splitting yet
    :param word:
    :param context:
    :return:
    """
    wiktionary_scraper = WiktionaryScraper()
    wiktionary_dict = wiktionary_scraper.scrape(word)

    model = AutoModel.from_pretrained("KBLab/bert-base-swedish-cased")
    tokenizer = AutoTokenizer.from_pretrained("KBLab/bert-base-swedish-cased")

    context_token_ids = tokenizer.encode(context)
    print(context_token_ids)

    context_tokens = tokenizer.convert_ids_to_tokens(context_token_ids)

    print(context_tokens)

    token_index = context_tokens.index(word)
    print(token_index)

    context_output = model(torch.tensor([context_token_ids]))

    for token_index in range(0, len(context_tokens)):
        print(token_index, context_tokens[token_index])

        contextualized_word_output = context_output.last_hidden_state[0, token_index]

        definition_embeddings = []
        cos = torch.nn.CosineSimilarity(dim=0)

        sentence_model = AutoModel.from_pretrained("KBLab/bert-base-swedish-cased")
        sentence_tokenizer = AutoTokenizer.from_pretrained(
            "KBLab/bert-base-swedish-cased"
        )

        possible_definitions = [
            definition["text"]
            for definition in wiktionary_dict["options"][0]["definitions"]
        ] + [
            "dryckeskärl, ofta av porslin, avsett att dricka (varmare vätskor) ur",
            "kopp",
            "koppar",
        ]

        for definition in possible_definitions:
            definition_tokens = sentence_tokenizer.encode(definition)
            definition_output = sentence_model(torch.tensor([definition_tokens]))
            definition_embeddings.append(definition_output.pooler_output[0])

            print(
                definition,
                ": ",
                cos(contextualized_word_output, definition_output.pooler_output[0]),
                torch.cdist(
                    contextualized_word_output.view(1, 768),
                    definition_output.pooler_output[0].view(1, 768),
                ),
            )

    # print(definition_embeddings)


if __name__ == "__main__":
    app()
