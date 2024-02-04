import { HTMLAttributes } from "react";
import React from "react";

const TaskButtonsContainer = (
  props: HTMLAttributes<HTMLDivElement>,
): React.JSX.Element => {
  return <div className="flex flex-row gap-1 mb-2 mt-2">{props.children}</div>;
};

export default TaskButtonsContainer;
