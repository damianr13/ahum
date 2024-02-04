import React, { useCallback, useMemo, useState } from "react";
import { Song } from "@/models/song";
import { TaskResponse } from "@/models/task-response";
import { extractIndex } from "@/utils/parse";
import TaskButton from "@/components/karaoke-viewer/tasks/components/task-button";
import TaskButtonsContainer from "@/components/karaoke-viewer/tasks/components/task-buttons-container";

export interface LineReorderingTaskProps {
  song: Song;
  line: string;
  onInput: (value: TaskResponse) => void;
}

interface LineOrderButtonProps {
  onSelected: () => void;
  isCorrect: boolean | undefined;
  selectionIndex: number | undefined;
  word: string;
}

const LineOrderButton = (props: LineOrderButtonProps) => {
  const { onSelected, word, isCorrect, selectionIndex } = props;

  console.log("Selection index", selectionIndex);
  return (
    <TaskButton
      onClick={onSelected}
      isCorrect={isCorrect}
      disabled={selectionIndex !== undefined}
    >
      {word}
      <sub>{selectionIndex !== -1 ? selectionIndex : ""}</sub>
    </TaskButton>
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

  const onSelected = useCallback(
    (index: number) => {
      if (!task) return;

      const newSelection = [...currentSelection, index];
      setCurrentSelection(newSelection);

      props.onInput({
        response: newSelection.map((i) => task.scrambled_line[i]).join(" "),
        done: newSelection.length === correctSelection.length,
      });
    },
    [currentSelection, props, task, correctSelection],
  );
  const selectionIndex = useCallback(
    (index: number) => {
      const resultFromJS = currentSelection.indexOf(index);
      return resultFromJS >= 0 ? resultFromJS : undefined;
    },
    [currentSelection],
  );

  return (
    <TaskButtonsContainer>
      {task?.scrambled_line.map((word, index) => (
        <LineOrderButton
          key={index}
          isCorrect={selectionValidity[currentSelection.indexOf(index)]}
          selectionIndex={selectionIndex(index)}
          onSelected={() => onSelected(index)}
          word={word}
        />
      ))}
    </TaskButtonsContainer>
  );
};

export default LineReorderingTaskView;
