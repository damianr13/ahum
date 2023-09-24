import random
import re
from functools import wraps

from Levenshtein import distance

from src.dictionary import load_dictionary_for_language
from src.schemas.song import SongWithLanguage, ProcessedSong
from src.schemas.tasks import WordSelectionTask, LineReorderingTask


def requires_dictionary(func):
    @wraps(func)
    def wrapper(self: "SongProcessor", *method_args, **method_kwargs):
        if not self.dictionary:
            self.dictionary = load_dictionary_for_language(self.song.language)
        return func(self, *method_args, **method_kwargs)

    return wrapper


def requires_words_from_lyrics(func):
    @wraps(func)
    def wrapper(self: "SongProcessor", *method_args, **method_kwargs):
        if not self.words_from_lyrics:
            self.words_from_lyrics = self._extract_words_from_lyrics()
        return func(self, *method_args, **method_kwargs)

    return wrapper


def requires_oov_words(func):
    @wraps(func)
    def wrapper(self: "SongProcessor", *method_args, **method_kwargs):
        if not self.oov_words:
            self.oov_words = self._find_oov_words()
        return func(self, *method_args, **method_kwargs)

    return wrapper


class SongProcessor:
    def __init__(self, song: SongWithLanguage):
        self.song = song
        self.lyrics = song.lyrics
        self.dictionary = None
        self.curated_lyrics = None
        self.words_from_lyrics = None
        self.oov_words = None
        self.processed_lyrics = None

        self.word_selection_tasks: list[WordSelectionTask] = []
        self.line_reordering_tasks: list[LineReorderingTask] = []

    def _extract_words_from_lyrics(self):
        curated_lyrics = self.lyrics.replace("<br>", "\n").replace("<br/>", "\n")

        # remove html tags and text within brackets from lyrics
        curated_lyrics = re.sub(r"<[^>]*>", " ", curated_lyrics)
        curated_lyrics = re.sub(r"\[[^]]*]", " ", curated_lyrics)
        # remove punctuation
        curated_lyrics = re.sub(r"[^\w\s]", " ", curated_lyrics)

        # remove multiple spaces, but keep newlines
        curated_lyrics = re.sub(r" +", " ", curated_lyrics)

        # normalize spaces
        curated_lyrics_words = re.sub(r"\s+", " ", curated_lyrics)

        self.curated_lyrics = curated_lyrics

        # split into words
        return [
            word
            for word in curated_lyrics_words.split(" ")
            if not word == "" and not word.isnumeric()
        ]

    def _find_oov_words(self):
        return [
            word
            for word in self.words_from_lyrics
            if (word not in self.dictionary and not word.lower() in self.dictionary)
        ]

    @requires_dictionary
    @requires_words_from_lyrics
    def create_word_selection_task(self, forced_word: str = None) -> "SongProcessor":
        exclusion_list = (
            self.oov_words
            + [task.target_word for task in self.word_selection_tasks]
            + [
                word
                for line_reordering_task in self.line_reordering_tasks
                for word in line_reordering_task.scrambled_line
            ]
        )

        word_to_replace = random.choice(
            [
                word
                for word in set(self.words_from_lyrics)
                if word not in exclusion_list and len(word) >= 5
            ]
        )
        if forced_word:
            word_to_replace = forced_word

        print("Word to replace")
        print(word_to_replace)

        # Find 2 other words in the dictionary that are close to this one
        alternatives = []

        for word in random.sample(self.dictionary, len(self.dictionary)):
            if word.lower() == word_to_replace.lower():
                continue

            current_distance = distance(word_to_replace, word)

            if current_distance <= 2:
                alternatives.append(word)
                if len(alternatives) == 2:
                    break

        alternatives.append(word_to_replace)
        new_task = WordSelectionTask(
            task_id=len(self.word_selection_tasks),
            target_word=word_to_replace,
            alternatives=random.sample(alternatives, len(alternatives)),
        )
        self.word_selection_tasks.append(new_task)

        return self

    @staticmethod
    def _select_one_unique(line_pool: list[str]) -> str:
        # Select a pure line that appears only once
        lines_count_dict = {}
        for line in line_pool:
            if line in lines_count_dict:
                lines_count_dict[line] += 1
            else:
                lines_count_dict[line] = 1

        unique_pure_lines = [
            line for line in lines_count_dict if lines_count_dict[line] == 1
        ]
        lines_pool = unique_pure_lines

        line_to_scramble = random.choice(lines_pool)
        return re.sub(r"\s+", " ", line_to_scramble)

    @requires_words_from_lyrics
    @requires_dictionary
    @requires_oov_words
    def create_line_reordering_task(self) -> "SongProcessor":
        all_lines = [line.strip() for line in self.curated_lyrics.splitlines()]

        # extract the lines containing no oov words
        pure_lines = [
            line
            for line in all_lines
            if not any(
                # Especially for french, after removing punctuation we are left of with 'j' and 'l'
                (len(oov_word) >= 2) and (oov_word in line)
                for oov_word in self.oov_words
            )
        ]

        try:
            line_to_scramble = self._select_one_unique(pure_lines)
        except IndexError:
            print("WARNING: No pure lines found")
            # If there are no pure lines, we select one that contains at least one oov word
            line_to_scramble = self._select_one_unique(all_lines)

        # scramble the line
        line_words = line_to_scramble.strip().split(" ")
        random.shuffle(line_words)
        scrambled_line = " ".join(line_words)

        new_task = LineReorderingTask(
            task_id=len(self.line_reordering_tasks),
            original_line=line_to_scramble,
            scrambled_line=scrambled_line.split(" "),
        )
        self.line_reordering_tasks.append(new_task)

        return self

    @requires_words_from_lyrics
    def mask_words_according_to_tasks(self) -> "SongProcessor":
        processed_lyrics = self.curated_lyrics

        self.processed_lyrics = processed_lyrics.strip()
        self.processed_lyrics = re.sub(r"\n{3,}", "\n\n", self.processed_lyrics)

        processed_lines = self.processed_lyrics.splitlines()
        processed_lines_original = processed_lines.copy()

        inserted_lines_count = 0
        word_tasks_handled = []
        for index, line in enumerate(processed_lines_original):
            updated_line = line

            # only update the real insertion count after all tasks have been handled
            lines_inserted_for_current_line = 0
            for task in self.line_reordering_tasks:
                if task.original_line == line:
                    updated_line = (
                        "_" * (len(line) // 2)
                        + f"lp{task.task_id}"
                        + "_" * (len(line) // 2)
                    )
                    processed_lines.insert(
                        index + inserted_lines_count + 1,
                        "__lrt{task_id}__".format(task_id=task.task_id),
                    )
                    lines_inserted_for_current_line += 1

            for task in self.word_selection_tasks:
                if task.target_word in line:
                    updated_line = updated_line.replace(
                        task.target_word,
                        "_" * (len(task.target_word) // 2)
                        + f"wp{task.task_id}"
                        + "_" * (len(task.target_word) // 2),
                    )
                    if task.task_id not in word_tasks_handled:
                        processed_lines.insert(
                            index + inserted_lines_count + 1, f"__wst{task.task_id}__",
                        )
                        word_tasks_handled.append(task.task_id)
                        lines_inserted_for_current_line += 1

            processed_lines[index + inserted_lines_count] = updated_line
            inserted_lines_count += lines_inserted_for_current_line

        self.processed_lyrics = "\n".join(processed_lines)

        return self

    def get_processed_song(self) -> ProcessedSong:
        return ProcessedSong(
            **{
                **self.song.model_dump(),
                "processed_lyrics": self.processed_lyrics,
                "word_selection_tasks": self.word_selection_tasks,
                "line_reordering_tasks": self.line_reordering_tasks,
            }
        )
