import { useEffect, useMemo, useState } from "react";
import { Button } from "@mui/material";
import { LineReorderingTask } from "@/models/song";
import { TaskResponse } from "@/models/task-response";

export interface LineReorderingTaskProps {
  task: LineReorderingTask;
  onInput: (value: TaskResponse) => void;
}

interface LineOrderButtonProps {
  onSelected: () => void;
  isSelected: boolean;
  isCorrect: boolean | undefined;
  selectionIndex: number | undefined;
  word: string;
}

const LineOrderButton = (props: LineOrderButtonProps) => {
  const {
    onSelected,
    word,
    isSelected,
    isCorrect,
    selectionIndex
  } = props;
  const backgroundColor = useMemo(() => {
    if (!isSelected) return "transparent";

    return isCorrect ? "green" : "red";
  }, [isSelected, isCorrect]);

  console.log(word, props)
  return (
    <Button
      variant="outlined"
      style={{
        color: "white",
        borderColor: "white",
        backgroundColor: backgroundColor,
      }}
      onClick={onSelected}
    >
      {word}
      <sub>{selectionIndex !== -1 ? selectionIndex : ""}</sub>
    </Button>
  );
};

const LineReorderingTaskView = (props: LineReorderingTaskProps) => {
  const [currentSelection, setCurrentSelection] = useState<number[]>([]);
  const correctSelection = useMemo(() => {
    if (!props.task) return [];
    return props.task.original_line.trim().split(" ");
  }, [props]);
  const selectionValidity = useMemo(() => {
    return currentSelection.map((wordIndex, index) => {
      return (
        props.task.scrambled_line[wordIndex].toLowerCase() ===
        correctSelection[index].toLowerCase()
      );
    });
  }, [currentSelection, correctSelection, props]);

  useEffect(() => {
    console.log("currentSelection", currentSelection);
    if (!props.task || currentSelection.length === 0) return;

    if (selectionValidity.some((valid) => !valid)) {
      props.onInput({
        response: currentSelection.join(" "),
        done: true,
      });
      return;
    }

    console.log("selections", currentSelection, correctSelection);
    props.onInput({
      response: currentSelection
        .map((i) => props.task.scrambled_line[i])
        .join(" "),
      done: currentSelection.length === correctSelection.length,
    });
  }, [currentSelection, props, selectionValidity, correctSelection]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        gap: "8px",
        justifyContent: "center",
        margin: "16px",
        maxWidth: "100%",
        flexWrap: "wrap",
      }}
    >
      {props.task.scrambled_line.map((word, index) => (
        <LineOrderButton
          key={index}
          isSelected={currentSelection.includes(index)}
          isCorrect={selectionValidity[currentSelection.indexOf(index)]}
          selectionIndex={currentSelection.indexOf(index)}
          onSelected={() => setCurrentSelection([...currentSelection, index])}
          word={word}
        />
      ))}
    </div>
  );
};

export default LineReorderingTaskView;
