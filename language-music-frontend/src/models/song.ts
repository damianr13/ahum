export interface LineReorderingTask {
  task_id: number;
  original_line: string;
  scrambled_line: string[];
}

export interface WordSelectionTask {
  task_id: number;
  target_word: string;
  alternatives: string[];
}

export interface Song {
  spotify_id: string;
  youtube_id: string;
  lyrics: string;
  processed_lyrics: string;

  line_reordering_tasks: LineReorderingTask[];
  word_selection_tasks: WordSelectionTask[];
}
