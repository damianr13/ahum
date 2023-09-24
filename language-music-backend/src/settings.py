from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    genius_api_access_token: str

    spotify_client_id: str
    spotify_client_secret: str

    youtube_api_key: str


@lru_cache()
def get_settings() -> Settings:
    return Settings(_env_file=".env", _env_file_encoding="utf-8")
