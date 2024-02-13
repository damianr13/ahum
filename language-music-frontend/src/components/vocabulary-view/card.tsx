import { VocabularyEntry } from "@/components/vocabulary-view/types";
import { useCallback, useState } from "react";

const VocabularyCard = (props: {
  word: string;
  vocabularyEntry: VocabularyEntry;
}) => {
  const { word, vocabularyEntry } = props;
  const [isExpanded, setIsExpanded] = useState(false);

  const renderCEFRLevel = useCallback((level?: number | null | string) => {
    if (level === null || level === undefined || typeof level === "string") {
      return <span className="font-bold text-cyan-300">??</span>;
    }
    const safeLevel = level as number;

    const cefrArray = ["A1", "A2", "B1", "B2", "C1", "C2"];
    const cefrColorArray = [
      "text-green-300",
      "text-green-600",
      "text-yellow-600",
      "text-orange-600",
      "text-rose-600",
      "text-red-600",
    ];
    return (
      <span className={`font-bold ${cefrColorArray[safeLevel - 1]}`}>
        {cefrArray[safeLevel - 1]}
      </span>
    );
  }, []);

  return (
    <div className="p-6 w-full text-white">
      <div
        className="bg-gray-600 p-4 rounded shadow-lg hover:shadow-2xl
        hover:translate-x-0.5 hover:translate-y-0.5 flex flex-col h-fit cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex flex-row">
          <div className="flex flex-col flex-grow basis-4">
            <div className="flex flex-row items-center flex-grow h-20 justify-center">
              <p className="text-4xl">{word}</p>
            </div>
          </div>
          <div className="flex flex-col w-1/5 justify-between items-end">
            <p className="">
              <span className="text-xs">CEFR</span>:{" "}
              {renderCEFRLevel(vocabularyEntry.cefr)}
            </p>
            {isExpanded ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="w-6 h-6"
              >
                <path
                  fill-rule="evenodd"
                  d="M11.47 7.72a.75.75 0 0 1 1.06 0l7.5 7.5a.75.75 0 1 1-1.06 1.06L12 9.31l-6.97 6.97a.75.75 0 0 1-1.06-1.06l7.5-7.5Z"
                  clip-rule="evenodd"
                />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="m19.5 8.25-7.5 7.5-7.5-7.5"
                />
              </svg>
            )}
          </div>
        </div>
        <div
          className={`${
            isExpanded ? "translate-y-0" : "-translate-y-full hidden"
          } transition-all delay-500 duration-500 pt-4 text-sm w-full`}
        >
          <hr className="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700" />
          <p className="whitespace-pre wrap overflow-x-clip">
            {JSON.stringify(vocabularyEntry, undefined, 4)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default VocabularyCard;
