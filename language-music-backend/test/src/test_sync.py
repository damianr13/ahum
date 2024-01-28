import json
import unittest

from src.sync import (
    clean_lyrics,
    extract_known_passages,
    print_sync_stats_debug,
    sync_words,
)


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

    def test_word_sync_perfect_match(self):
        one_segment = [
            {
                "id": 5,
                "seek": 0,
                "start": 65.586,
                "end": 69.626,
                "text": " En ung av dem som svick vänfors",
                "tokens": [
                    51514,
                    2193,
                    29038,
                    1305,
                    1371,
                    3307,
                    17342,
                    618,
                    371,
                    4029,
                    69,
                    830,
                    51764,
                ],
                "temperature": 0.0,
                "avg_logprob": -0.48396933833255046,
                "compression_ratio": 1.3566433566433567,
                "no_speech_prob": 0.35624364018440247,
                "confidence": 0.619,
                "words": [
                    {"text": "En", "start": 65.586, "end": 66.026, "confidence": 0.953},
                    {
                        "text": "ung",
                        "start": 66.026,
                        "end": 66.346,
                        "confidence": 0.688,
                    },
                    {"text": "av", "start": 66.346, "end": 66.866, "confidence": 0.258},
                    {"text": "dem", "start": 66.866, "end": 67.306, "confidence": 0.64},
                    {
                        "text": "som",
                        "start": 67.306,
                        "end": 67.886,
                        "confidence": 0.941,
                    },
                    {
                        "text": "svick",
                        "start": 67.886,
                        "end": 68.54599999999999,
                        "confidence": 0.534,
                    },
                    {
                        "text": "vänfors",
                        "start": 68.54599999999999,
                        "end": 69.626,
                        "confidence": 0.647,
                    },
                ],
            }
        ]
        one_known_passage = [(0, 7)]  # the exact number of words as in the passage
        lyrics = "En ung av dem som svick vänfors"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(synced_words[-1][-1][0], 68.54599999999999)
        self.assertEqual(synced_words[-1][-1][1], 69.626)

    def test_word_sync_stt_fewer_words(self):
        one_segment = [
            {
                "id": 2,
                "seek": 0,
                "start": 116.888,
                "end": 120.86800000000001,
                "text": " En drömmamma sömma fan",
                "tokens": [
                    51114,
                    2193,
                    1224,
                    973,
                    2174,
                    335,
                    1696,
                    12643,
                    29577,
                    3429,
                    51364,
                ],
                "temperature": 0.0,
                "avg_logprob": -0.4803428034628591,
                "compression_ratio": 1.2032520325203253,
                "no_speech_prob": 0.3031805455684662,
                "confidence": 0.535,
                "words": [
                    {
                        "text": "En",
                        "start": 116.888,
                        "end": 117.36800000000001,
                        "confidence": 0.189,
                    },
                    {
                        "text": "drömmamma",
                        "start": 117.36800000000001,
                        "end": 119.208,
                        "confidence": 0.725,
                    },
                    {
                        "text": "sömma",
                        "start": 119.208,
                        "end": 120.28800000000001,
                        "confidence": 0.368,
                    },
                    {
                        "text": "fan",
                        "start": 120.28800000000001,
                        "end": 120.86800000000001,
                        "confidence": 0.699,
                    },
                ],
            }
        ]
        one_known_passage = [(0, 6)]  # STT detected 4 words but there are in fact 6
        lyrics = "En dröm om mammas ömma famn"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(synced_words[-1][-1][0], 120.28800000000001)
        self.assertEqual(synced_words[-1][-1][1], 120.86800000000001)

    def test_words_sync_stt_more_words(self):
        one_segment = [
            {
                "id": 1,
                "seek": 0,
                "start": 47.146,
                "end": 50.986000000000004,
                "text": " Svar till hjärtat, svar har sött",
                "tokens": [
                    50614,
                    318,
                    8517,
                    4288,
                    23731,
                    24802,
                    267,
                    11,
                    262,
                    8517,
                    2233,
                    12643,
                    6319,
                    50814,
                ],
                "temperature": 0.0,
                "avg_logprob": -0.48396933833255046,
                "compression_ratio": 1.3566433566433567,
                "no_speech_prob": 0.35624364018440247,
                "confidence": 0.506,
                "words": [
                    {
                        "text": "Svar",
                        "start": 47.146,
                        "end": 47.626,
                        "confidence": 0.345,
                    },
                    {
                        "text": "till",
                        "start": 47.626,
                        "end": 48.126,
                        "confidence": 0.905,
                    },
                    {
                        "text": "hjärtat,",
                        "start": 48.126,
                        "end": 49.286,
                        "confidence": 0.832,
                    },
                    {
                        "text": "svar",
                        "start": 49.286,
                        "end": 50.106,
                        "confidence": 0.532,
                    },
                    {
                        "text": "har",
                        "start": 50.106,
                        "end": 50.426,
                        "confidence": 0.209,
                    },
                    {
                        "text": "sött",
                        "start": 50.426,
                        "end": 50.986000000000004,
                        "confidence": 0.391,
                    },
                ],
            },
        ]
        one_known_passage = [(0, 5)]  # the STT has 5 words, but the lyrics have 6
        lyrics = "Svar till: Hjärtat talar sant"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(synced_words[-1][-1][0], 50.426)
        self.assertEqual(synced_words[-1][-1][1], 50.986000000000004)

    def test_words_sync_stt_fewer_words_last(self):
        one_segment = [
            {
                "id": 2,
                "seek": 0,
                "start": 51.346000000000004,
                "end": 55.706,
                "text": " En pessimist i sitt livsform",
                "tokens": [50814, 2193, 37399, 468, 741, 43709, 11477, 82, 837, 51064],
                "temperature": 0.0,
                "avg_logprob": -0.48396933833255046,
                "compression_ratio": 1.3566433566433567,
                "no_speech_prob": 0.35624364018440247,
                "confidence": 0.803,
                "words": [
                    {
                        "text": "En",
                        "start": 51.346000000000004,
                        "end": 51.986000000000004,
                        "confidence": 0.97,
                    },
                    {
                        "text": "pessimist",
                        "start": 51.986000000000004,
                        "end": 53.606,
                        "confidence": 0.997,
                    },
                    {"text": "i", "start": 53.606, "end": 54.146, "confidence": 0.947},
                    {
                        "text": "sitt",
                        "start": 54.146,
                        "end": 54.666,
                        "confidence": 0.997,
                    },
                    {
                        "text": "livsform",
                        "start": 54.666,
                        "end": 55.706,
                        "confidence": 0.574,
                    },
                ],
            },
        ]
        one_known_passage = [(0, 7)]
        lyrics = "En pessimist i sitt livs form Jag"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(
            len(lyrics.split(" ")),
            len([s for sync_list in synced_words for s in sync_list]),  # flatten
        )

    def test_stt_much_more_words(self):
        one_segment = [
            {
                "id": 4,
                "seek": 0,
                "start": 60.745999999999995,
                "end": 65.166,
                "text": " En röd som jordings kärlek störst",
                "tokens": [
                    51314,
                    2193,
                    367,
                    29747,
                    3307,
                    361,
                    765,
                    1109,
                    350,
                    2713,
                    29205,
                    42554,
                    372,
                    51514,
                ],
                "temperature": 0.0,
                "avg_logprob": -0.48396933833255046,
                "compression_ratio": 1.3566433566433567,
                "no_speech_prob": 0.35624364018440247,
                "confidence": 0.531,
                "words": [
                    {
                        "text": "En",
                        "start": 60.745999999999995,
                        "end": 61.306,
                        "confidence": 0.988,
                    },
                    {
                        "text": "röd",
                        "start": 61.306,
                        "end": 61.786,
                        "confidence": 0.346,
                    },
                    {
                        "text": "som",
                        "start": 61.786,
                        "end": 62.206,
                        "confidence": 0.989,
                    },
                    {
                        "text": "jordings",
                        "start": 62.206,
                        "end": 63.266,
                        "confidence": 0.426,
                    },
                    {
                        "text": "kärlek",
                        "start": 63.266,
                        "end": 64.386,
                        "confidence": 0.692,
                    },
                    {
                        "text": "störst",
                        "start": 64.386,
                        "end": 65.166,
                        "confidence": 0.41,
                    },
                ],
            }
        ]
        one_known_passage = [(0, 3)]
        lyrics = "En utomjordings kärlekstörst"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(
            len(lyrics.split(" ")),
            len([s for sync_list in synced_words for s in sync_list]),  # flatten
        )

    def test_stt_much_more_words_2(self):
        one_segment = [
            {
                "id": 8,
                "seek": 2800,
                "start": 79.46600000000001,
                "end": 83.866,
                "text": " Ser i dig, ser i dig dit",
                "tokens": [50814, 4210, 741, 2528, 11, 816, 741, 2528, 6176, 51114],
                "temperature": 0.0,
                "avg_logprob": -0.36205676107695606,
                "compression_ratio": 1.0740740740740742,
                "no_speech_prob": 0.02123287320137024,
                "confidence": 0.687,
                "words": [
                    {
                        "text": "Ser",
                        "start": 79.46600000000001,
                        "end": 79.74600000000001,
                        "confidence": 0.65,
                    },
                    {
                        "text": "i",
                        "start": 79.74600000000001,
                        "end": 80.146,
                        "confidence": 0.632,
                    },
                    {
                        "text": "dig,",
                        "start": 80.146,
                        "end": 80.926,
                        "confidence": 0.945,
                    },
                    {
                        "text": "ser",
                        "start": 81.306,
                        "end": 82.186,
                        "confidence": 0.989,
                    },
                    {
                        "text": "i",
                        "start": 82.186,
                        "end": 82.48599999999999,
                        "confidence": 0.993,
                    },
                    {
                        "text": "dig",
                        "start": 82.48599999999999,
                        "end": 83.386,
                        "confidence": 0.943,
                    },
                    {
                        "text": "dit",
                        "start": 83.386,
                        "end": 83.866,
                        "confidence": 0.201,
                    },
                ],
            },
        ]
        one_known_passage = [(0, 5)]
        lyrics = "Sälj dig, sälj dig dyrt"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(
            len(lyrics.split(" ")),
            len([s for sync_list in synced_words for s in sync_list]),  # flatten
        )

    def test_stt_much_more_words_3(self):
        one_segment = [
            {
                "id": 3,
                "seek": 0,
                "start": 122.06800000000001,
                "end": 125.92800000000001,
                "text": " En utsom jordingskärleks törst",
                "tokens": [
                    51364,
                    2193,
                    2839,
                    24154,
                    361,
                    765,
                    1109,
                    74,
                    2713,
                    306,
                    1694,
                    256,
                    2311,
                    372,
                    51614,
                ],
                "temperature": 0.0,
                "avg_logprob": -0.4803428034628591,
                "compression_ratio": 1.2032520325203253,
                "no_speech_prob": 0.3031805455684662,
                "confidence": 0.592,
                "words": [
                    {
                        "text": "En",
                        "start": 122.06800000000001,
                        "end": 122.28800000000001,
                        "confidence": 0.5,
                    },
                    {
                        "text": "utsom",
                        "start": 122.28800000000001,
                        "end": 122.748,
                        "confidence": 0.463,
                    },
                    {
                        "text": "jordingskärleks",
                        "start": 122.748,
                        "end": 125.14800000000001,
                        "confidence": 0.64,
                    },
                    {
                        "text": "törst",
                        "start": 125.14800000000001,
                        "end": 125.92800000000001,
                        "confidence": 0.615,
                    },
                ],
            }
        ]
        one_known_passage = [(0, 3)]
        lyrics = "En utomjordings kärlekstörst"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(
            len(lyrics.split(" ")),
            len([s for sync_list in synced_words for s in sync_list]),  # flatten
        )

    def test_stt_way_off(self):
        one_segment = [
            {
                "id": 7,
                "seek": 2500,
                "start": 140.08800000000002,
                "end": 144.368,
                "text": " Säg hur det är, säg hur det är ditt",
                "tokens": [
                    51014,
                    318,
                    50041,
                    2756,
                    1141,
                    3775,
                    11,
                    15316,
                    70,
                    2756,
                    1141,
                    3775,
                    274,
                    593,
                    51264,
                ],
                "temperature": 0.0,
                "avg_logprob": -0.5166380456153382,
                "compression_ratio": 1.150943396226415,
                "no_speech_prob": 0.034337013959884644,
                "confidence": 0.532,
                "words": [
                    {
                        "text": "Säg",
                        "start": 140.08800000000002,
                        "end": 140.168,
                        "confidence": 0.413,
                    },
                    {
                        "text": "hur",
                        "start": 140.168,
                        "end": 140.548,
                        "confidence": 0.315,
                    },
                    {
                        "text": "det",
                        "start": 140.548,
                        "end": 141.168,
                        "confidence": 0.476,
                    },
                    {
                        "text": "är,",
                        "start": 141.168,
                        "end": 141.268,
                        "confidence": 0.474,
                    },
                    {
                        "text": "säg",
                        "start": 141.488,
                        "end": 142.62800000000001,
                        "confidence": 0.898,
                    },
                    {
                        "text": "hur",
                        "start": 142.62800000000001,
                        "end": 142.868,
                        "confidence": 0.999,
                    },
                    {
                        "text": "det",
                        "start": 142.868,
                        "end": 143.568,
                        "confidence": 0.984,
                    },
                    {
                        "text": "är",
                        "start": 143.568,
                        "end": 143.948,
                        "confidence": 0.538,
                    },
                    {
                        "text": "ditt",
                        "start": 143.948,
                        "end": 144.368,
                        "confidence": 0.317,
                    },
                ],
            }
        ]
        one_known_passage = [(0, 6)]
        lyrics = "ny Sälj dig, sälj dig dyrt"

        synced_words = sync_words(one_known_passage, one_segment, lyrics)

        self.assertEqual(
            len(lyrics.split(" ")),
            len([s for sync_list in synced_words for s in sync_list]),  # flatten
        )

    def test_end_to_end_word_sync(self):
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
        synced_words = sync_words(known_passages, data["segments"], just_lyrics)

        self.assertEqual(
            len([w for w in just_lyrics.split(" ") if w]),
            len([s for sync_list in synced_words for s in sync_list]),  # flatten
        )
