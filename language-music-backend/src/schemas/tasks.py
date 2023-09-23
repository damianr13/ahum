from pydantic import BaseModel


class WordSelectionTask(BaseModel):
    task_id: int
    target_word: str
    alternatives: list[str]


class LineReorderingTask(BaseModel):
    task_id: int
    original_line: str
    scrambled_line: list[str]
