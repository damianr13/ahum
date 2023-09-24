import { WordSelectionTask } from "@/models/song";
import { Button } from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { TaskResponse } from "@/models/task-response";

export interface WordSelectionTaskProps {
  task: WordSelectionTask;
  onInput: (value: TaskResponse) => void;
}

interface WordSelectionButtonProps {
  selectedWord: string | undefined;
  onSelect: () => void;
  alternative: string;
  targetWord: string;
}

const WordSelectionButton = (props: WordSelectionButtonProps) => {
  const { selectedWord, onSelect, alternative, targetWord } =
    props;
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

  useEffect(() => {
    if (!props.task || !selectedWord) return;

    props.onInput({
      response: selectedWord,
      done: true,
    });
  }, [selectedWord, props]);

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
      {props.task.alternatives.map((alternative, index) => (
        <WordSelectionButton
          key={index}
          selectedWord={selectedWord}
          onSelect={() => setSelectedWord(alternative)}
          alternative={alternative}
          targetWord={props.task.target_word}
        />
      ))}
    </div>
  );
};

export default WordSelectionTaskView;
