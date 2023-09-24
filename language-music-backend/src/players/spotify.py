import spotipy
from spotipy import SpotifyClientCredentials

from src.players.abstract import AbstractPlayer
from src.settings import get_settings


class SpotifyClient(AbstractPlayer):
    spotify = None

    def __init__(self):
        settings = get_settings()

        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=settings.spotify_client_id,
                client_secret=settings.spotify_client_secret,
            )
        )

    def fetch_song_extended_title(self, song_id: str):
        uri = f"spotify:track:{song_id}"

        spotify_track = self.spotify.track(uri)
        return spotify_track["artists"][0]["name"] + " - " + spotify_track["name"]

    def search_for_song(self, query: str) -> str:
        results = self.spotify.search(q=query, type="track", limit=1)
        return results["tracks"]["items"][0]["id"]
