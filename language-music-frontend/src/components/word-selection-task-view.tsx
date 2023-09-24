import { WordSelectionTask } from "@/models/song";
import { Button } from "@mui/material";
import {useEffect, useMemo, useState} from "react";
import {TaskResponse} from "@/models/task-response";

export interface WordSelectionTaskProps {
    task: WordSelectionTask;
    onInput: (value: TaskResponse) => void;
}

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
  }, [selectedWord, props])

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
      {props.task.alternatives.map((alternative, index) => {
        const isDisabled = useMemo(() => {
            return selectedWord !== undefined;
        }, [selectedWord])
        const backgroundColor = useMemo(() => {
            if (alternative === selectedWord && alternative !== props.task.target_word) return "red";
            if (alternative === props.task.target_word && selectedWord !== undefined) return "green";
            if (isDisabled) {
                return "gray";
            }
            return "transparent";
        }, [selectedWord, props.task.target_word, alternative, isDisabled])
        return (
          <Button
            key={index}
            variant="outlined"
            sx={{
              color: "white",
              borderColor: "white",
              backgroundColor: { backgroundColor },
            }}
            onClick={() => setSelectedWord(alternative)}
            disabled={isDisabled}
          >
            {alternative}
          </Button>
        );
      })}
    </div>
  );
};

export default WordSelectionTaskView;
