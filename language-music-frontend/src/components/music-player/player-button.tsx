import React, { HTMLAttributes } from "react";

const PlayerButton = (props: HTMLAttributes<HTMLButtonElement>) => {
  const { children } = props;

  return (
    <button
      className="bg-gray-700 hover:bg-gray-600 p-2 rounded-full text-white"
      {...props}
    >
      {children}
    </button>
  );
};

export default PlayerButton;
