from pydantic import BaseModel

from src.schemas.tasks import LineReorderingTask, WordSelectionTask


class Song(BaseModel):
    spotify_id: str
    lyrics: str


class SongWithLanguage(Song):
    language: str


class ProcessedSong(SongWithLanguage):
    processed_lyrics: str
    word_selection_tasks: list[WordSelectionTask]
    line_reordering_tasks: list[LineReorderingTask]
