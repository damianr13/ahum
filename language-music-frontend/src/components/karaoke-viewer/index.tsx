import React, { useEffect, useMemo, useState } from "react";
import { Song } from "@/models/song";
import WordSelectionTaskView from "@/components/karaoke-viewer/tasks/word-selection-task-view";
import LineReorderingTaskView from "@/components/karaoke-viewer/tasks/line-reordering-task-view";
import { TaskResponse } from "@/models/task-response";
import { extractIndex } from "@/utils/parse";

type LyricLine = {
  word: string;
  time: number; // in seconds
};

type KaraokeLyricsProps = {
  song: Song;
  currentTime: number;
  onSeek: (time: number) => void;
};

interface WordComponentProps extends KaraokeLyricsProps {
  item: LyricLine;
  line: LyricLine[];
  lineIndex: number;
  wordIndex: number;
  parsedLyrics: LyricLine[][];
  taskResponses: {
    [key: string]: TaskResponse;
  };

  onTaskUpdated(response: TaskResponse, taskIdentifier: string): void;
}

const parseLrc = (lrcString: string): LyricLine[][] => {
  const lines = lrcString.split("\n");
  return lines.map((line) => {
    const wordTimestampPairs =
      line.match(/\[(\d{2}:\d{2}.\d{2})\](\S+)/g) || [];
    return wordTimestampPairs.map((pair) => {
      const [_, timestamp, word] = pair.match(/\[(.*?)\](.*)/) || [];
      const [minutes, seconds] = timestamp.split(":");
      const timeInSeconds = parseFloat(minutes) * 60 + parseFloat(seconds);
      return { word, time: timeInSeconds };
    });
  });
};

const WordComponent = (props: WordComponentProps): React.JSX.Element => {
  const {
    currentTime,
    item,
    line,
    lineIndex,
    wordIndex,
    onSeek,
    taskResponses,
    song,
    parsedLyrics,
    onTaskUpdated,
  } = props;

  const isActive =
    currentTime >= item.time &&
    (!line[wordIndex + 1] || currentTime < line[wordIndex + 1].time) &&
    currentTime <=
      (lineIndex + 1 < parsedLyrics.length &&
      parsedLyrics[lineIndex + 1].length > 0
        ? parsedLyrics[lineIndex + 1][0].time
        : item.time + 3);
  let clickableWordClass =
    "hover:text-gray-400 cursor-pointer " +
    "transition duration-150 ease-in-out transform hover:scale-105";

  let processedWord = item.word;
  if (processedWord.indexOf("__lp") !== -1) {
    clickableWordClass +=
      " underline-offset-2 decoration-2 underline whitespace-pre";
    const taskIdentifier = processedWord.replaceAll("_", "");
    const taskIndex = extractIndex(processedWord, "lp");

    if (taskIndex !== undefined && taskIdentifier in taskResponses) {
      const task = song.line_reordering_tasks[taskIndex];

      if (!taskResponses[taskIdentifier].done) {
        processedWord = taskResponses[taskIdentifier].response;
        processedWord += " ".repeat(
          task.original_line.length -
            taskResponses[taskIdentifier].response.length,
        );
      } else {
        processedWord = task.original_line;
      }
    } else {
      processedWord = processedWord.replace(/lp\d+/g, "").replaceAll("_", " ");
    }
  }
  if (processedWord.indexOf("__wp") !== -1) {
    clickableWordClass +=
      " underline-offset-2 decoration-2 underline whitespace-pre";
    const taskIdentifier = processedWord.replaceAll("_", "");
    const taskIndex = extractIndex(processedWord, "wp");
    if (taskIndex !== undefined && taskIdentifier in taskResponses) {
      processedWord = song.word_selection_tasks[taskIndex].target_word;
    } else {
      processedWord = processedWord.replace(/wp\d+/g, "").replaceAll("_", " ");
    }
  }

  if (processedWord.indexOf("__wst") !== -1) {
    const taskIndex = extractIndex(processedWord, "wst");
    const task = props.song.word_selection_tasks.find((task) => {
      return task.task_id === taskIndex;
    });
    if (!task) {
      return <></>;
    }
    return (
      <WordSelectionTaskView
        key={wordIndex}
        task={task}
        onInput={(response) => onTaskUpdated(response, `wp${taskIndex}`)}
      />
    );
  }
  if (processedWord.indexOf("__lrt") !== -1) {
    const taskIndex = extractIndex(processedWord, "lrt");
    return (
      <LineReorderingTaskView
        key={wordIndex}
        line={processedWord}
        song={song}
        onInput={(response) => onTaskUpdated(response, `lp${taskIndex}`)}
      />
    );
  }
  const activeClass = `my-1 ${clickableWordClass} ${
    isActive ? "font-bold text-lg word-active" : "text-base"
  }`;

  return (
    <>
      <span
        id={`word-${wordIndex}`}
        key={wordIndex}
        className={activeClass}
        onClick={() => onSeek(item.time)}
      >
        {processedWord}
      </span>
      <span>&nbsp;</span>
    </>
  );
};

const KaraokeLyrics: React.FC<KaraokeLyricsProps> = (
  props: KaraokeLyricsProps,
) => {
  /**
   * The component that shows the lyrics for the song with synced timestamps.
   *
   * Note: this used to scroll to each word, but there were some issues with that:
   * - if the user tried to scroll to some other part of the song they would be blocked
   * - if this component is used in a tab component, the scroll would affect the horizontal position, and put the tab
   * component in a weird state
   */

  const { song, currentTime, onSeek } = props;
  const { processed_lyrics: lyrics, lyrics_url: lyricsUrl } = song;
  const [parsedLyrics, setParsedLyrics] = useState<LyricLine[][]>([]);

  const [taskResponses, setTaskResponses] = useState<{
    [key: string]: TaskResponse;
  }>({});

  useEffect(() => {
    setParsedLyrics(parseLrc(lyrics));
  }, [lyrics]);

  const renderedLyrics = useMemo(() => {
    return parsedLyrics.map((line, lineIndex) => (
      <p key={lineIndex}>
        {line.map((item, wordIndex) => (
          <WordComponent
            key={wordIndex}
            item={item}
            line={line}
            lineIndex={lineIndex}
            wordIndex={wordIndex}
            parsedLyrics={parsedLyrics}
            taskResponses={taskResponses}
            onTaskUpdated={(response, taskIdentifier) => {
              console.log("Task solutions", taskResponses);
              console.log("Task updated", response, taskIdentifier);
              setTaskResponses({
                ...taskResponses,
                [taskIdentifier]: response,
              });
            }}
            {...props}
          />
        ))}
        {line.length == 0 && <br />}
      </p>
    ));
  }, [parsedLyrics, taskResponses, props]);

  return (
    <div>
      <div>{renderedLyrics}</div>

      {/*Attribution*/}
      <div className="text-xs text-gray-400 mt-2 italic">
        Lyrics by:{" "}
        <a
          className="underline"
          href={lyricsUrl ?? "https://genius.com"}
          target="_blank"
          rel="noreferrer"
        >
          Genius.com
        </a>
      </div>
    </div>
  );
};

export default KaraokeLyrics;
