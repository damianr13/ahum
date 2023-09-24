import { useEffect, useMemo, useState } from "react";
import { Button } from "@mui/material";
import { LineReorderingTask } from "@/models/song";
import { TaskResponse } from "@/models/task-response";

export interface LineReorderingTaskProps {
  task: LineReorderingTask;
  onInput: (value: TaskResponse) => void;
}

interface LineOrderButtonProps {
  currentSelection: number[];
  setCurrentSelection: (value: number[]) => void;
  index: number;
  word: string;
  selectionValidity: boolean[];
}

const LineOrderButton = (props: LineOrderButtonProps) => {
  const {
    currentSelection,
    setCurrentSelection,
    index,
    word,
    selectionValidity,
  } = props;

  const selectionIndex = useMemo(
    () => currentSelection.indexOf(index),
    [currentSelection, index],
  );
  const backgroundColor = useMemo(() => {
    if (selectionIndex === -1) return "transparent";
    if (selectionValidity[selectionIndex]) return "green";
    return "red";
  }, [selectionIndex, selectionValidity]);
  return (
    <Button
      key={index}
      variant="outlined"
      sx={{
        color: "white",
        borderColor: "white",
        backgroundColor: { backgroundColor },
      }}
      onClick={() => setCurrentSelection([...currentSelection, index])}
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
      }}
    >
      {props.task.scrambled_line.map((word, index) => (
        <LineOrderButton
          key={index}
          currentSelection={currentSelection}
          setCurrentSelection={setCurrentSelection}
          index={index}
          word={word}
          selectionValidity={selectionValidity}
        />
      ))}
    </div>
  );
};

export default LineReorderingTaskView;
