from typing import List, Tuple

from src.sync.utils import seek_to_human_readable_time


def apply_formatting(lyrics: str, synced_words: List[List[Tuple[float, float]]]):
    """
    Apply formatting to the lyrics.

    Should rely on the structure of the lyrics, not on the one defined by the segments in the synced_words.

    :param lyrics:
    :param synced_words:
    :return:
    """
    result = ""
    synced_index = 0

    flat_synced_words = [w for part in synced_words for w in part]

    for line in lyrics.splitlines():
        for word in line.split():
            start = seek_to_human_readable_time(flat_synced_words[synced_index][0])
            result += f"[{start}]{word} "
            synced_index += 1

        result += "\n"

    return result
