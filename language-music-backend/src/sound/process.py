from src.sound.fetch import download, convert
from src.sound.separation import extract_voice, split
from src.sound.transcription import transcribe


def process(youtube_id: str, language: str):
    """
    Applies all the processing necessary to go from a song id on youtube to the synchronized lyrics

    All the intermediate files (including the final transcriptions) are stored in local storage.

    :param youtube_id: the song id on youtube
    :param language:  the language of the lyrics
    :return:
    """
    working_dir = f"data/songs/{youtube_id}"

    download(working_dir)

    convert(working_dir)

    extract_voice(working_dir)

    split(working_dir)

    transcribe(working_dir, language)
