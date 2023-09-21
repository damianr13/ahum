from fastapi import FastAPI

from src import spotify, firestore
from src.genius import get_song_url, get_lyrics
from src.schemas.song import Song

db = firestore.init_firestore()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/lyrics")
def fetch_lyrics(q: str):
    song_url = get_song_url(q)
    lyrics = get_lyrics(song_url)
    return {"lyrics": lyrics}


@app.get("/song", response_model=Song)
def fetch_song(langauge: str):
    pass
