from pydantic import BaseModel


class Song(BaseModel):
    spotify_id: str
    lyrics: str
