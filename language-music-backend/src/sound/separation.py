import os.path

import torch
import torchaudio
from torchaudio.pipelines import HDEMUCS_HIGH_MUSDB_PLUS
from torchaudio.transforms import Fade

from src.sound.utils import CONVERTED_FILE_NAME, VOCALS_FILE_NAME


def __separate_sources(
    model,
    mix,
    segment=10.0,
    overlap=0.1,
    device=None,
    sample_rate=44100,
):
    """
    Apply model to a given mixture. Use fade, and add segments together in order to add model segment by segment.

    Source: https://pytorch.org/audio/stable/tutorials/hybrid_demucs_tutorial.html

    Args:
        segment (int): segment length in seconds
        device (torch.device, str, or None): if provided, device on which to
            execute the computation, otherwise `mix.device` is assumed.
            When `device` is different from `mix.device`, only local computations will
            be on `device`, while the entire tracks will be stored on `mix.device`.
    """
    if device is None:
        device = mix.device
    else:
        device = torch.device(device)

    batch, channels, length = mix.shape

    chunk_len = int(sample_rate * segment * (1 + overlap))
    start = 0
    end = chunk_len
    overlap_frames = overlap * sample_rate
    fade = Fade(fade_in_len=0, fade_out_len=int(overlap_frames), fade_shape="linear")

    final = torch.zeros(batch, len(model.sources), channels, length, device=device)

    while start < length - overlap_frames:
        chunk = mix[:, :, start:end]
        with torch.no_grad():
            out = model.forward(chunk)
        out = fade(out)
        final[:, :, :, start:end] += out
        if start == 0:
            fade.fade_in_len = int(overlap_frames)
            start += int(chunk_len - overlap_frames)
        else:
            start += chunk_len
        end += chunk_len
        if end >= length:
            fade.fade_out_len = 0
    return final


def extract_voice(target_location: str) -> str:
    bundle = HDEMUCS_HIGH_MUSDB_PLUS
    model = bundle.get_model()
    device = torch.device("cpu")
    model.to(device)

    # We download the audio file from our storage. Feel free to download another file and use audio from a specific path
    song_file = os.path.join(target_location, CONVERTED_FILE_NAME)
    waveform, sample_rate = torchaudio.load(
        song_file
    )  # replace SAMPLE_SONG with desired path for different song
    waveform = waveform.to(device)

    if sample_rate != 44100:
        print("Warn: Resampling to 44100Hz, from ", sample_rate, "Hz")
        waveform = torchaudio.functional.resample(waveform, sample_rate, 44100)
        sample_rate = 44100

    # parameters
    segment: int = 10
    overlap = 0.1

    print("Separating track")

    ref = waveform.mean(0)
    waveform = (waveform - ref.mean()) / ref.std()  # normalization

    sources = __separate_sources(
        model,
        waveform[None],
        device=device,
        segment=segment,
        overlap=overlap,
    )[0]
    sources = sources * ref.std() + ref.mean()

    sources_list = model.sources
    sources = list(sources)

    audios = dict(zip(sources_list, sources))

    output_file_name = os.path.join(target_location, VOCALS_FILE_NAME)
    torchaudio.save(output_file_name, audios["vocals"], sample_rate)

    return output_file_name
