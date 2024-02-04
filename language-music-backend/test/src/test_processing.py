import json
import re
import unittest
from typing import Tuple

from src.processing import SongProcessor, apply_lyric_curation
from src.schemas.song import SongWithLanguage, ProcessedSong


def _process_song(input_file: str) -> Tuple[ProcessedSong, SongProcessor]:
    with open(input_file, "r") as f:
        song_json = json.load(f)
    song = SongWithLanguage(**song_json)
    song_processor = SongProcessor(song)

    processed_song = (
        song_processor.create_line_reordering_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .mask_words_according_to_tasks()
        .get_processed_song()
    )

    return processed_song, song_processor


class ProcessorTest(unittest.TestCase):
    def test_word_replacement_duplicate_words(self):
        with open("test/data/viva_la_dealer.json", "r") as f:
            song_json = json.load(f)
        song = SongWithLanguage(**song_json)
        song_processor = SongProcessor(song)

        processed_song = (
            song_processor.create_line_reordering_task()
            .create_word_selection_task("Stoff")
            .create_word_selection_task()
            .create_word_selection_task("verkauft")
            .mask_words_according_to_tasks()
            .get_processed_song()
        )

        self.assertTrue("Stoff" not in processed_song.processed_lyrics)
        self.assertTrue("verkauft" not in processed_song.processed_lyrics)

        self.assertEqual(
            processed_song.line_reordering_tasks[0].original_line.strip(),
            processed_song.line_reordering_tasks[0].original_line,
        )

    def __test_with_lrc_format_one_iteration(self, song: SongWithLanguage):
        song_processor = SongProcessor(song, keep_lrc=True)

        processed_song = (
            song_processor.create_line_reordering_task()
            .create_word_selection_task()
            .create_word_selection_task()
            .create_word_selection_task()
            .mask_words_according_to_tasks()
            .get_processed_song()
        )

        processed_lines = processed_song.processed_lyrics.split("\n")
        lines_without_timestamps = [
            line for line in processed_lines if not line.startswith("[") and line != ""
        ]

        self.assertEqual(lines_without_timestamps, [])

        lines_with_ordering_tasks = [line for line in processed_lines if "__lp" in line]
        self.assertEqual(len(lines_with_ordering_tasks), 1)

        line_with_ordering_task = lines_with_ordering_tasks[0]
        line_timestamp_match = re.search(
            "(\\[\\d+:\\d+\\.\\d+])", line_with_ordering_task
        )
        self.assertIsNotNone(line_timestamp_match)
        line_timestamp = line_timestamp_match.group(1)

        original_line = next(
            line
            for line in processed_song.lyrics.split("\n")
            if line.startswith(line_timestamp)
        )
        original_line_curated = apply_lyric_curation(original_line).strip()
        line_ordering_original = processed_song.line_reordering_tasks[0].original_line

        self.assertEqual(line_ordering_original, original_line_curated)
        for word_task in processed_song.word_selection_tasks:
            self.assertTrue(
                word_task.target_word not in processed_song.processed_lyrics.split()
            )

    def test_with_lrc_format(self):
        with open("test/data/sunnavind.json", "r") as f:
            song_json = json.load(f)
        song = SongWithLanguage(**song_json)

        for i in range(50):
            """
            Due to the randomness included in the processor (selecting a random line or random words) we run this
            test multiple times to make sure it doesn't fail.
            """

            self.__test_with_lrc_format_one_iteration(song)

    def test_missing_line_reordering_task(self):
        with open("test/data/sunnavind.json", "r") as f:
            song_json = json.load(f)
        song = SongWithLanguage(**song_json)

        song_processor = SongProcessor(song, keep_lrc=True)
        processed_song = (
            song_processor.create_line_reordering_task(
                forced_line="Ur våra koppar i Berså hey"
            )
            .mask_words_according_to_tasks()
            .get_processed_song()
        )
        processed_lines = processed_song.processed_lyrics.split("\n")

        self.assertEqual(len(processed_song.line_reordering_tasks), 1)

        lines_with_ordering_tasks = [line for line in processed_lines if "__lp" in line]
        self.assertEqual(len(lines_with_ordering_tasks), 1)
