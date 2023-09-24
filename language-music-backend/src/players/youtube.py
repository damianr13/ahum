from src.players.abstract import AbstractPlayer
from googleapiclient.discovery import build

from src.settings import get_settings


class YoutubeClient(AbstractPlayer):
    def __init__(self):
        settings = get_settings()
        self.youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)

    def search_for_song(self, query: str) -> str:
        search_response = (
            self.youtube.search()
            .list(q=query, part="id", maxResults=1, type="video")
            .execute()
        )

        return search_response["items"][0]["id"]["videoId"]

    def fetch_song_extended_title(self, song_id: str) -> str:
        search_response = (
            self.youtube.videos().list(id=song_id, part="snippet").execute()
        )

        return search_response["items"][0]["snippet"]["title"]
