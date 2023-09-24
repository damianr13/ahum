from abc import ABC, abstractmethod


class AbstractPlayer(ABC):
    @abstractmethod
    def search_for_song(self, query: str) -> str:
        """Search for a song and return the song id"""
        pass

    @abstractmethod
    def fetch_song_extended_title(self, song_id: str) -> str:
        """Fetch the song extended title"""
        pass
