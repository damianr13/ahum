import json
import os.path
from typing import Union

import typer

from src import firestore
from src.genius import get_song_url, get_lyrics
from src.players import spotify, youtube
from src.players.utils import convert_id
from src.processing import SongProcessor
from src.schemas.song import SongWithLanguage, ProcessedSong
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
from structlog import get_logger

logger = get_logger()
app = typer.Typer()


def __sync_lyrics_for_song(song: SongWithLanguage):
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


def __process_from_scratch(
    title: str, language: str
) -> Union[ProcessedSong, SongWithLanguage]:
    spotify_client = spotify.SpotifyClient()
    youtube_client = youtube.YoutubeClient()

    logger.info("Searching for song", title=title)
    spotify_id = spotify_client.search_for_song(title)
    youtube_id = youtube_client.search_for_song(title)

    logger.info("Searching for lyrics")
    genius_url = get_song_url(title)
    lyrics = get_lyrics(genius_url)

    logger.info("Saving song")
    song = SongWithLanguage(
        spotify_id=spotify_id,
        youtube_id=youtube_id,
        lyrics=lyrics,
        language=language,
        lyrics_url=genius_url,
    )
    json.dump(
        song.model_dump(), open(f"data/songs/last_song.json", "w", encoding="utf-8")
    )

    try:
        processor = SongProcessor(song)

        return (
            processor.create_line_reordering_task()
            .create_word_selection_task()
            .create_word_selection_task()
            .create_word_selection_task()
            .mask_words_according_to_tasks()
            .get_processed_song()
        )
    except ValueError:  # Unknown language
        return song


@app.command()
def insert_song(title: str, language: str):
    processed_song = __process_from_scratch(title, language)
    spotify_id = processed_song.spotify_id

    db = firestore.init_firestore()

    db.collection("songs").document(f"spotify-{spotify_id}").set(
        processed_song.model_dump()
    )


@app.command()
def process_locally(title: str, language: str):
    processed_song = __process_from_scratch(title, language)
    song_dir = os.path.join("data", "songs", processed_song.youtube_id)
    if not os.path.exists(song_dir):
        os.makedirs(song_dir)

    with open(os.path.join(song_dir, "doc.json"), "w", encoding="utf-8") as f:
        json.dump(processed_song.model_dump(), f, ensure_ascii=False, indent=4)

    transcribe_song(processed_song.youtube_id, language)

    __sync_lyrics_for_song(processed_song)


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


if __name__ == "__main__":
    app()
