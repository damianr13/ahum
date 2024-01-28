import pydub
import numpy as np

ORIGINAL_FILE_NAME = "original.webm"
CONVERTED_FILE_NAME = "converted.wav"
VOCALS_FILE_NAME = "vocals.wav"
SPLITS_DIR_NAME = "splits"
SPLITS_TIMESTAMPS_FILE_NAME = "timestamps.txt"
TRANSCRIPTION_FILE_NAME = "transcription.json"

SPLITS_PADDING = 2000  # ms


def convert_to_numpy(audio: pydub.AudioSegment):
    return (
        np.array(audio.get_array_of_samples(), dtype=np.float32).reshape(
            (-1, audio.channels)
        )
        / (1 << (8 * audio.sample_width - 1)),
        audio.frame_rate,
    )
