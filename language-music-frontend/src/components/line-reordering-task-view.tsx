import { useEffect, useMemo, useState } from "react";
import { Button } from "@mui/material";
import { Song } from "@/models/song";
import { TaskResponse } from "@/models/task-response";
import { extractIndex } from "@/utils/parse";

export interface LineReorderingTaskProps {
  song: Song;
  line: string;
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
  const { onSelected, word, isSelected, isCorrect, selectionIndex } = props;
  const backgroundColor = useMemo(() => {
    if (!isSelected) return "transparent";

    return isCorrect ? "green" : "red";
  }, [isSelected, isCorrect]);

  console.log(word, props);
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
  const { song, line } = props;

  const task = useMemo(
    () =>
      song.line_reordering_tasks.find((task) => {
        return task.task_id === extractIndex(line, "lrt");
      }),
    [song, line],
  );

  const correctSelection = useMemo(() => {
    if (!task) return [];
    return task.original_line.trim().split(" ");
  }, [task]);
  const selectionValidity = useMemo(() => {
    return currentSelection.map((wordIndex, index) => {
      return (
        task?.scrambled_line[wordIndex].toLowerCase() ===
        correctSelection[index].toLowerCase()
      );
    });
  }, [currentSelection, correctSelection, task]);

  useEffect(() => {
    console.log("currentSelection", currentSelection);
    if (!task || currentSelection.length === 0) return;

    if (selectionValidity.some((valid) => !valid)) {
      props.onInput({
        response: currentSelection.join(" "),
        done: true,
      });
      return;
    }

    console.log("selections", currentSelection, correctSelection);
    props.onInput({
      response: currentSelection.map((i) => task.scrambled_line[i]).join(" "),
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
      {task?.scrambled_line.map((word, index) => (
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
