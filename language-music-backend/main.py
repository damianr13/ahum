"""
The main file for the functions.

For the FastAPI application start point check backend.py
"""
import base64
import json

import functions_framework
from cloudevents.http import CloudEvent

from src import genius, firestore
from src.players import spotify
import firebase_admin.firestore

db = firestore.init_firestore()


@functions_framework.cloud_event
def populate_spotify_song(event: CloudEvent, context=None):
    encoded_data = event.data["message"]["data"]
    data = json.loads(base64.b64decode(encoded_data))

    song_id = data["spotify_id"]
    song_language = data["language"]

    spotify_client = spotify.SpotifyClient()
    extended_title = spotify_client.fetch_song_extended_title(song_id)

    genius_url = genius.get_song_url(extended_title)
    lyrics = genius.get_lyrics(genius_url)

    doc_ref = db.collection("songs").document(f"spotify-{song_id}")
    result = doc_ref.set(
        {
            "spotify_id": song_id,
            "lyrics": lyrics,
            "genius_url": genius_url,
            "fetch_time": firebase_admin.firestore.firestore.SERVER_TIMESTAMP,
            "language": song_language,
        }
    )

    print("Result: ", result)

    return "OK"
