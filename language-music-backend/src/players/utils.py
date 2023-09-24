from src.players.abstract import AbstractPlayer


def convert_id(
    source: AbstractPlayer, destination: AbstractPlayer, song_id: str
) -> str:
    """Convert the song id from one player to another"""
    song_extended_title = source.fetch_song_extended_title(song_id)
    return destination.search_for_song(song_extended_title)
