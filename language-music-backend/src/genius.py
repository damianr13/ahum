import requests

from src.settings import get_settings
from bs4 import BeautifulSoup

GENIUS_API_BASE_URL = "https://api.genius.com"


def get_song_url(song_name: str) -> str:
    settings = get_settings()

    response = requests.get(
        f"{GENIUS_API_BASE_URL}/search",
        params={"q": song_name},
        headers={"Authorization": f"Bearer {settings.genius_api_access_token}"},
    )

    response.raise_for_status()

    response_json = response.json()

    song_url = response_json["response"]["hits"][0]["result"]["url"]

    return song_url


def get_lyrics(song_url: str) -> str:
    response = requests.get(song_url)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_elements = soup.findAll("div", {"data-lyrics-container": "true"})

    lyrics = ""
    for lyrics_element in lyrics_elements:
        lyrics += lyrics_element.encode_contents().decode("utf-8")

    return lyrics
