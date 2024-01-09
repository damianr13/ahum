import json
import os.path

import whisper_timestamped as whisper
from tqdm import tqdm

from src.sound.utils import (
    SPLITS_DIR_NAME,
    SPLITS_TIMESTAMPS_FILE_NAME,
    TRANSCRIPTION_FILE_NAME,
)
from structlog import get_logger

logger = get_logger()


def transcribe(target_location: str, language: str):
    logger.info("Transcribing audio")
    splits_dir = os.path.join(target_location, SPLITS_DIR_NAME)
    model = whisper.load_model("openai/whisper-medium")
    logger.debug("Model loaded")

    # read timestamp delays
    with open(os.path.join(splits_dir, SPLITS_TIMESTAMPS_FILE_NAME), "r") as f:
        chunk_timestamps = [
            [float(i) for i in line.split(" ")]
            for line in f.readlines()
            if line.strip()
        ]
    logger.debug("Timestamps loaded", chunk_timestamps=chunk_timestamps)

    full_transcription = {"segments": [], "text": ""}

    # list files in splits_dir
    for i in tqdm(range(len(chunk_timestamps)), desc="Transcribing"):
        file_name = f"{i}.wav"

        result = whisper.transcribe(
            model,
            audio=os.path.join(splits_dir, file_name),
            task="transcribe",
            initial_prompt="lyrics:",
            language=language,
        )
        timestamp_adjustment = chunk_timestamps[i][0] / 1000

        result_adjusted = {
            "text": result["text"],
            "segments": [
                {
                    **s,
                    "end": s["end"] + timestamp_adjustment,
                    "start": s["start"] + timestamp_adjustment,
                    "words": [
                        {
                            **w,
                            "end": w["end"] + timestamp_adjustment,
                            "start": w["start"] + timestamp_adjustment,
                        }
                        for w in s["words"]
                    ],
                }
                for s in result["segments"]
            ],
        }

        full_transcription = {
            "text": full_transcription["text"] + result_adjusted["text"],
            "segments": full_transcription["segments"] + result_adjusted["segments"],
        }

    with open(os.path.join(target_location, TRANSCRIPTION_FILE_NAME), "w") as f:
        json.dump(full_transcription, f)
