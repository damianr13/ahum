import json
import math
import re
from typing import Tuple, Dict, List

from thefuzz import fuzz


def read_toy_lyrics_data() -> Tuple[Dict, str]:
    with open("data/fr_timestamped.json", "r") as f:
        data = json.load(f)

    with open("data/fr_plain.txt", "r") as f:
        lyrics = f.read()

    lyrics = lyrics.strip().replace("\\s+", " ")

    return data, lyrics


def clean_lyrics(lyrics: str) -> str:
    """
    We scrape lyrics, and they might come with their own HTML code and square brackets, which we don't want.

    We want the vanilla lyrics to match them with the whisper output.
    :param lyrics:
    :return:
    """

    # Replace tags and square brackets with spaces instead of empty strings to prevent word concatenation
    no_html = re.sub(r"<[^>]*>", " ", lyrics)
    no_brackets = re.sub(r"\[.*?]", " ", no_html)
    return no_brackets.replace("\\s+", " ").strip()


def __explore_around_passage(
    lyrics: str,
    segment_text: str,
    longest_passage: Tuple[int, int],
    start: int = 0,
) -> Tuple[int, int]:
    """
    Given a passage, explore around it to see if there is a longer / shorter passage that has a higher score
    """
    max_score = fuzz.ratio(
        " ".join(lyrics.split()[longest_passage[0] : longest_passage[1]]), segment_text
    )

    # remove tokens from the left until the score decreases
    while longest_passage[0] < longest_passage[1]:
        new_start = longest_passage[0] + 1
        new_passage = " ".join(lyrics.split()[new_start : longest_passage[1]])
        new_score = fuzz.ratio(new_passage, segment_text)

        if new_score < max_score:
            break

        longest_passage = (new_start, longest_passage[1])
        max_score = new_score

    # remove tokens from the right until the score decreases
    while longest_passage[0] < longest_passage[1]:
        new_end = longest_passage[1] - 1
        new_passage = " ".join(lyrics.split()[longest_passage[0] : new_end])
        new_score = fuzz.ratio(new_passage, segment_text)

        if new_score < max_score:
            break

        longest_passage = (longest_passage[0], new_end)
        max_score = new_score

    # prepend tokens to the left until the score decreases
    while longest_passage[0] > start:
        new_start = longest_passage[0] - 1
        new_passage = " ".join(lyrics.split()[new_start : longest_passage[1]])
        new_score = fuzz.ratio(new_passage, segment_text)

        if new_score < max_score:
            break

        longest_passage = (new_start, longest_passage[1])
        max_score = new_score

    # append tokens to the right until the score decreases
    while longest_passage[1] < len(lyrics.split()):
        new_end = longest_passage[1] + 1
        new_passage = " ".join(lyrics.split()[longest_passage[0] : new_end])
        new_score = fuzz.ratio(new_passage, segment_text)

        if new_score < max_score:
            break

        longest_passage = (longest_passage[0], new_end)
        max_score = new_score

    return longest_passage


def search_for_segment(
    lyrics: str, segment_text: str, start: int = 0, matching_threshold: int = 75
) -> Tuple[int, int]:
    """
    Search for a segment in the lyrics, starting at the given index
    :param lyrics:
    :param segment_text:
    :param start:
    :param matching_threshold:
    :return:
    """
    total_words = len(lyrics.split())

    current_passage_start = start
    segment_size = len(segment_text.split())

    # Maybe whisper splits some words
    # For example we don't want to skip if the segment size if 6 and the total words count is 5
    # This happens when we recursively search through the gaps after the first iteration on the full lyrics
    window_size = len(segment_text.split()) - math.ceil(segment_size / 5)
    if window_size + start > total_words:
        # How?
        # Whisper hallucinates with very long sequences of words, we just skip those.
        return start, start

    score_matrix = {}

    while current_passage_start < len(lyrics.split()) - window_size:
        current_passage_end = current_passage_start + window_size
        current_passage = " ".join(
            lyrics.split()[current_passage_start:current_passage_end]
        )

        passage_score = fuzz.ratio(current_passage, segment_text)
        # Adjust the score to favor passages that are closer to the start of the lyrics
        passage_score = passage_score * (
            1 - (current_passage_start - start) / (len(lyrics.split()) - start) * 0.2
        )

        score_matrix[(current_passage_start, current_passage_end)] = passage_score

        current_passage_start += 1

    if not score_matrix:
        """
        This happens when the transformer hallucinates something at the end of the song.

        We are already cutting out silent segments from the vocals, but we append and prepend 2 seconds to the output
        from pydub, to make sure we allow for the word to start and finish properly. This might allow some space for
        the transformer to hallucinate though.
        """
        return start, start

    # find the max score
    max_score = max(score_matrix.values())

    if max_score < matching_threshold:
        # If the max score is too low, we don't want to return anything
        return start, start

    # Get the passage with the max score, and the lowest start index, but longest length
    longest_passage = min(
        [k for k, v in score_matrix.items() if v == max_score],
        key=lambda x: x[0] * 1000 - (x[1] - x[0]),
    )
    longest_passage = __explore_around_passage(
        lyrics, segment_text, longest_passage, start=start
    )

    return longest_passage


def __identify_gaps(
    known_passages: List[Tuple[int, int]], lyrics: str
) -> List[Tuple[int, int]]:
    gaps = [
        (known_passages[i][1], known_passages[i + 1][0])
        for i in range(len(known_passages) - 1)
        if known_passages[i + 1][0] - known_passages[i][1] > 0
    ]
    if known_passages[-1][1] < len(lyrics.split()):
        gaps.append((known_passages[-1][1], len(lyrics.split())))

    return gaps


def __recursively_map_passages(
    relevant_segments: List[Dict], lyrics: str, recursive_ttl: int = 3
) -> List[Tuple[int, int]]:
    known_passages = []
    for segment in relevant_segments:
        longest_passage = search_for_segment(
            lyrics,
            segment["text"].strip(),
            start=0 if len(known_passages) == 0 else known_passages[-1][1],
            matching_threshold=50 + 10 * recursive_ttl,
        )

        known_passages.append(longest_passage)

    gaps = __identify_gaps(known_passages, lyrics)

    missed_segments = {
        i: known_passages[i]
        for i in range(len(known_passages))
        if known_passages[i][1] - known_passages[i][0] == 0
    }

    gap_segments_mapping = {
        g: [s for s, p in missed_segments.items() if p[0] >= g[0] and p[1] <= g[1]]
        for g in gaps
    }

    if recursive_ttl < 0:
        """
        Finally if we have gaps with only 1 corresponding segment we allow it.
        """
        for gap, segments in gap_segments_mapping.items():
            if len(segments) == 1:
                known_passages[segments[0]] = (gap[0], gap[1])

        return known_passages

    for gap, segments in gap_segments_mapping.items():
        if len(segments) == 0:
            continue

        partial_lyrics = " ".join(lyrics.split()[gap[0] : gap[1]])
        gap_known_passages = __recursively_map_passages(
            relevant_segments=[relevant_segments[s] for s in segments],
            lyrics=partial_lyrics,
            recursive_ttl=recursive_ttl - 1,
        )

        for i, p in enumerate(gap_known_passages):
            known_passages[segments[i]] = (p[0] + gap[0], p[1] + gap[0])

    return known_passages


def extract_known_passages(
    relevant_segments: List[Dict], lyrics: str
) -> List[Tuple[int, int]]:
    known_passages = __recursively_map_passages(relevant_segments, lyrics)

    missed_segment_starts = [
        known_passages[i][0]
        for i in range(len(known_passages))
        if known_passages[i][1] - known_passages[i][0] == 0
    ]
    if not missed_segment_starts or missed_segment_starts[0] == len(lyrics.split()):
        """
        What this means:

        We covered all the segments (except for maybe some hallucination at the end.
        In this case we assume it's safe to "patch" the gaps, by appending the words we skip to the end of the
        most appropriate segment.
        """

        return [
            (known_passages[i][0], known_passages[i + 1][0])
            for i in range(len(known_passages) - 1)
        ] + [known_passages[-1]]

    return known_passages


def print_sync_stats_debug(
    known_passages: List[Tuple[int, int]], relevant_segments: List[Dict], lyrics: str
):
    for i in range(len(known_passages)):
        print(known_passages[i])
        print(" ".join(lyrics.split()[known_passages[i][0] : known_passages[i][1]]))
        print(relevant_segments[i]["text"].strip())
        print("\n")

    max_gap = max(
        [
            known_passages[i + 1][0] - known_passages[i][1]
            for i in range(len(known_passages) - 1)
        ]
    )
    print(
        "Covered up to index",
        known_passages[-1][1],
        "out of",
        len(lyrics.split()),
        ", max gap:",
        max_gap,
    )
