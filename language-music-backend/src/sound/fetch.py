import subprocess

import pytube
import os

from src.sound.utils import ORIGINAL_FILE_NAME, CONVERTED_FILE_NAME
from structlog import get_logger

logger = get_logger()


def download(target_location: str) -> str:
    logger.info("Downloading youtube audio", target_location=target_location)
    if target_location.endswith("/"):
        target_location = target_location[:-1]

    youtube_id = target_location.split("/")[-1]
    yt = pytube.YouTube(f"https://www.youtube.com/watch?v={youtube_id}")
    yt.streams.filter(type="audio", mime_type="audio/webm").order_by(
        "abr"
    ).desc().first().download(target_location, filename=ORIGINAL_FILE_NAME)

    return os.path.join(target_location, ORIGINAL_FILE_NAME)


def convert(target_location: str) -> str:
    logger.info("Converting to wav")
    input_file_name = os.path.join(target_location, ORIGINAL_FILE_NAME)
    output_file_name = os.path.join(target_location, CONVERTED_FILE_NAME)
    command = [
        "ffmpeg",
        "-y",  # skip questions
        "-i",
        input_file_name,
        "-ac",  # stereo, 2 audio channels
        "2",
        "-ar",  # sample rate, 44100 same as HDemucs training
        "44100",
        output_file_name,
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    return output_file_name
