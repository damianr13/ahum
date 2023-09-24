import json
import unittest
from typing import Tuple

from src.processing import SongProcessor
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

    def test_french_song(self):
        processed_song, song_processor = _process_song("test/data/sur_ma_route.json")

        # Check that we reached the end of the song processing
        self.assertTrue(True)

    def test_swedish_song(self):
        processed_song, song_processor = _process_song("test/data/dom_andra.json")

        # Check that we reached the end of the song processing
        self.assertTrue(True)
