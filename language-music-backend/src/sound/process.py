from src.sound.fetch import download, convert
from src.sound.separation import extract_voice


def process(youtube_id: str):
    """
    Applies all the processing necessary to go from a song id on youtube to the synchronized lyrics

    :return: TODO
    """
    working_dir = f"data/songs/{youtube_id}"

    download(working_dir)

    convert(working_dir)

    extract_voice(working_dir)

    """
    TODO: 
    
    1. Split the voices audio to remove silent segments
    2. Go through whisper to extract lyrics timestamps
    3. Sync text from Whisper with original text
    4. Find a good format to store the data
    """
