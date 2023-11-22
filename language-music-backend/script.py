from typing import Tuple, Dict

from thefuzz import fuzz
import json

import typer

from src import firestore
from src.genius import get_song_url, get_lyrics
from src.players import spotify, youtube
from src.players.utils import convert_id
from src.processing import SongProcessor
from src.schemas.song import SongWithLanguage

app = typer.Typer()


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


@app.command()
def insert_song(title: str, language: str):
    print(title)
    print(language)

    spotify_client = spotify.SpotifyClient()
    youtube_client = youtube.YoutubeClient()

    spotify_id = spotify_client.search_for_song(title)
    youtube_id = youtube_client.search_for_song(title)

    genius_url = get_song_url(title)
    lyrics = get_lyrics(genius_url)

    song = SongWithLanguage(
        spotify_id=spotify_id,
        youtube_id=youtube_id,
        lyrics=lyrics,
        language=language,
    )
    json.dump(song.model_dump(), open(f"data/last_song.json", "w", encoding="utf-8"))

    processor = SongProcessor(song)

    processed_song = (
        processor.create_line_reordering_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .mask_words_according_to_tasks()
        .get_processed_song()
    )

    db = firestore.init_firestore()

    db.collection("songs").document(f"spotify-{spotify_id}").set(
        processed_song.model_dump()
    )


def __read_lyrics_data() -> Tuple[Dict, str]:
    with open("data/fr_timestamped.json", "r") as f:
        data = json.load(f)

    with open("data/fr_plain.txt", "r") as f:
        lyrics = f.read()

    lyrics = lyrics.strip().replace("\\s+", " ")

    return data, lyrics


def __search_for_segment(
    lyrics: str, segment_text: str, start: int = 0
) -> Tuple[int, int]:
    # Idea to improve this: use a sliding window to find the best passage
    # Then look around that passage (add/subtract words to the left and right) to see if the score improves
    # We would have to try to append and subtract words from the passage, and see if the score improves
    current_passage_start = start

    score_matrix = {}

    while current_passage_start < len(lyrics.split()) - 1:
        current_passage_end = current_passage_start + 1
        while current_passage_end < len(lyrics.split()):
            current_passage = " ".join(
                lyrics.split()[current_passage_start:current_passage_end]
            )

            passage_score = fuzz.ratio(current_passage, segment_text)
            score_matrix[(current_passage_start, current_passage_end)] = passage_score

            current_passage_end += 1

        current_passage_start += 1

    # find the max score
    max_score = max(score_matrix.values())

    # Get the passage with the max score, and the lowest start index, but longest length
    longest_passage = min(
        [k for k, v in score_matrix.items() if v == max_score],
        key=lambda x: x[0] * 1000 - (x[1] - x[0]),
    )

    return longest_passage


@app.command()
def find_one_segment(index: int):
    data, lyrics = __read_lyrics_data()

    first_segment = data["segments"][index]

    longest_passage = __search_for_segment(lyrics, first_segment["text"])

    print(longest_passage)
    print(" ".join(lyrics.split()[longest_passage[0] : longest_passage[1]]))
    print(first_segment["text"])


@app.command()
def find_all_relevant_segments():
    data, lyrics = __read_lyrics_data()

    relevant_segments = data["segments"][:12]
    known_passages = []
    for segment in relevant_segments:
        longest_passage = __search_for_segment(
            lyrics,
            segment["text"],
            start=0 if len(known_passages) == 0 else known_passages[-1][1],
        )

        known_passages.append(longest_passage)
        print(longest_passage)

    print(known_passages)
    for i in range(len(known_passages)):
        print(" ".join(lyrics.split()[known_passages[i][0] : known_passages[i][1]]))
        print(relevant_segments[i]["text"])
        print("\n")


if __name__ == "__main__":
    app()
