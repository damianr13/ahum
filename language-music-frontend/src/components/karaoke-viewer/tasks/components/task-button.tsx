import React, { HTMLAttributes, useEffect, useMemo, useState } from "react";

interface TaskButtonProps extends HTMLAttributes<HTMLButtonElement> {
  isCorrect?: boolean;
  disabled?: boolean;
}

const TaskButton = (props: TaskButtonProps): React.JSX.Element => {
  const [buttonAnimation, setButtonAnimation] = useState("");

  const bgClass = useMemo(() => {
    if (props.isCorrect === undefined) {
      return "bg-transparent";
    }
    if (props.isCorrect) {
      return "bg-lime-700";
    } else {
      return "bg-red-700";
    }
  }, [props.isCorrect]);

  useEffect(() => {
    if (props.isCorrect === undefined) {
      return;
    }
    if (!props.isCorrect) {
      setButtonAnimation("animate-wiggle");
    } else {
      setButtonAnimation("animate-bounce-fast");
    }
    setTimeout(() => {
      setButtonAnimation("");
    }, 500);
  }, [props.isCorrect]);

  return (
    <button
      disabled={props.disabled}
      className={
        bgClass +
        " " +
        buttonAnimation +
        " enabled:hover:bg-sky-600 py-2 px-2 enabled:hover:border-transparent rounded text-xs " +
        "disabled:opacity-50 disabled:cursor-not-allowed" +
        " " +
        props.className
      }
      {...props}
    >
      {props.children}
    </button>
  );
};

export default TaskButton;
