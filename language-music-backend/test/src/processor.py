import json
import unittest
from src.processing import SongProcessor
from src.schemas.song import SongWithLanguage


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
        )

        self.assertTrue("Stoff" not in processed_song.processed_lyrics)
        self.assertTrue("verkauft" not in processed_song.processed_lyrics)

        self.assertEqual(
            processed_song.line_reordering_tasks[0].original_line.strip(),
            processed_song.line_reordering_tasks[0].original_line,
        )
