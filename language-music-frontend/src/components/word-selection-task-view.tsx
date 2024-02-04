import { Song } from "@/models/song";
import { Button } from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { TaskResponse } from "@/models/task-response";
import { extractIndex } from "@/utils/parse";

export interface WordSelectionTaskProps {
  song: Song;
  line: string;
  onInput: (value: TaskResponse) => void;
}

interface WordSelectionButtonProps {
  selectedWord: string | undefined;
  onSelect: () => void;
  alternative: string;
  targetWord: string;
}

const WordSelectionButton = (props: WordSelectionButtonProps) => {
  const { selectedWord, onSelect, alternative, targetWord } = props;
  const isDisabled = useMemo(() => {
    return selectedWord !== undefined;
  }, [selectedWord]);
  const backgroundColor = useMemo(() => {
    if (alternative === selectedWord && alternative !== targetWord)
      return "red";
    if (alternative === targetWord && selectedWord !== undefined)
      return "green";
    if (isDisabled) {
      return "gray";
    }
    return "transparent";
  }, [selectedWord, targetWord, alternative, isDisabled]);
  return (
    <Button
      variant="outlined"
      style={{
        color: "white",
        borderColor: "white",
        backgroundColor: backgroundColor,
      }}
      onClick={onSelect}
      disabled={isDisabled}
    >
      {alternative}
    </Button>
  );
};

const WordSelectionTaskView = (props: WordSelectionTaskProps) => {
  const [selectedWord, setSelectedWord] = useState<string | undefined>(
    undefined,
  );
  const task = props.song.word_selection_tasks.find((task) => {
    return task.task_id === extractIndex(props.line, "wst");
  });

  useEffect(() => {
    if (!task || !selectedWord) return;

    props.onInput({
      response: selectedWord,
      done: true,
    });
  }, [selectedWord, task, props]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        gap: "8px",
        justifyContent: "center",
        margin: "16px",
      }}
    >
      {task?.alternatives.map((alternative, index) => (
        <WordSelectionButton
          key={index}
          selectedWord={selectedWord}
          onSelect={() => setSelectedWord(alternative)}
          alternative={alternative}
          targetWord={task.target_word}
        />
      ))}
    </div>
  );
};

export default WordSelectionTaskView;
