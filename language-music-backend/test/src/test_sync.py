import json
import unittest

from src.sync import clean_lyrics, extract_known_passages, print_sync_stats_debug


class SyncTest(unittest.TestCase):
    def test_with_gap_iteration(self):
        """
        We know this test is difficult because whisper doesn't properly get the correct swedish words from the lyrics

        The fuzzy matching score is low for some segments, and we require further exploration of the leftover
        gaps to get the correct mapping
        :return:
        """

        with open("test/data/sync/dom_andra/lyrics.txt", "r") as f:
            lyrics = f.read()
        with open("test/data/sync/dom_andra/transcription.json", "r") as f:
            data = json.load(f)

        just_lyrics = clean_lyrics(lyrics)

        """
        TODO: Because of the greedy strategy in `__explore_around_passage` some segments cover less words then they 
        should. 
        
        Example: 
        "Var att vi blev sångomandra, vi blev sångomandra, vi blev sångomandra"
        """

        known_passages = extract_known_passages(data["segments"], just_lyrics)

        longest_gap = max(
            [
                known_passages[i + 1][0] - known_passages[i][1]
                for i in range(len(known_passages) - 1)
            ]
        )

        try:
            self.assertEqual(longest_gap, 0)
        except AssertionError:
            print_sync_stats_debug(
                known_passages, relevant_segments=data["segments"], lyrics=just_lyrics
            )
            raise
