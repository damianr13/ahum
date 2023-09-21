import spotipy
from spotipy import SpotifyClientCredentials

from src.settings import get_settings


class SpotifyClient:
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
