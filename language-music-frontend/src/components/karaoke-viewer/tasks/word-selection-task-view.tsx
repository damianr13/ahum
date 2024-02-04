import { WordSelectionTask } from "@/models/song";
import React, { useCallback, useMemo, useState } from "react";
import { TaskResponse } from "@/models/task-response";
import TaskButton from "@/components/karaoke-viewer/tasks/components/task-button";
import TaskButtonsContainer from "@/components/karaoke-viewer/tasks/components/task-buttons-container";

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
  const { selectedWord, onSelect, alternative, targetWord } = props;
  const isDisabled = useMemo(() => {
    return selectedWord !== undefined;
  }, [selectedWord]);
  const isCorrect = useMemo(() => {
    if (selectedWord === undefined) return undefined;
    if (alternative === targetWord) {
      return true;
    }

    if (selectedWord === alternative) {
      return false;
    }

    return undefined;
  }, [selectedWord, targetWord, alternative]);
  return (
    <TaskButton onClick={onSelect} isCorrect={isCorrect} disabled={isDisabled}>
      {alternative}
    </TaskButton>
  );
};

const WordSelectionTaskView = (props: WordSelectionTaskProps) => {
  const [selectedWord, setSelectedWord] = useState<string | undefined>(
    undefined,
  );
  const { task } = props;

  const onSelect = useCallback(
    (alternative: string) => {
      setSelectedWord(alternative);
      props.onInput({
        response: alternative,
        done: true,
      });
    },
    [props],
  );

  return (
    <TaskButtonsContainer>
      {task?.alternatives.map((alternative, index) => (
        <WordSelectionButton
          key={index}
          selectedWord={selectedWord}
          onSelect={() => onSelect(alternative)}
          alternative={alternative}
          targetWord={task.target_word}
        />
      ))}
    </TaskButtonsContainer>
  );
};

export default WordSelectionTaskView;
