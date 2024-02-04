import React, { useEffect, useState } from "react";
import { Song } from "@/models/song";
import WordSelectionTaskView from "@/components/word-selection-task-view";
import LineReorderingTaskView from "@/components/line-reordering-task-view";
import { TaskResponse } from "@/models/task-response";

type LyricLine = {
  word: string;
  time: number; // in seconds
};

type KaraokeLyricsProps = {
  song: Song;
  currentTime: number;
  onSeek: (time: number) => void;

  wordRenderer?: (word: string, isActive: boolean) => React.JSX.Element;
};

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

const KaraokeLyrics: React.FC<KaraokeLyricsProps> = (
  props: KaraokeLyricsProps,
) => {
  const { song, currentTime, onSeek, wordRenderer } = props;
  const { processed_lyrics: lyrics, lyrics_url: lyricsUrl } = song;
  const [parsedLyrics, setParsedLyrics] = useState<LyricLine[][]>([]);

  useEffect(() => {
    setParsedLyrics(parseLrc(lyrics));
  }, [lyrics]);

  useEffect(() => {
    const element = window.document.getElementsByClassName("word-active")[0];
    if (!element) {
      return;
    }
    // Scroll to element
    element.scrollIntoView({
      behavior: "smooth",
      block: "start",
      inline: "start",
    });
  }, [currentTime]);

  const renderLyrics = () => {
    return parsedLyrics.map((line, lineIndex) => (
      <p key={lineIndex}>
        {line.map((item, wordIndex) => {
          const isActive =
            currentTime >= item.time &&
            (!line[wordIndex + 1] || currentTime < line[wordIndex + 1].time) &&
            currentTime <=
              (lineIndex + 1 < parsedLyrics.length &&
              parsedLyrics[lineIndex + 1].length > 0
                ? parsedLyrics[lineIndex + 1][0].time
                : item.time + 3);
          const clickableWordClass =
            "hover:text-gray-400 cursor-pointer " +
            "transition duration-150 ease-in-out transform hover:scale-105";
          const activeClass = `my-1 ${clickableWordClass} ${
            isActive ? "font-bold text-lg word-active" : "text-base"
          }`;

          let processedWord = item.word;
          if (processedWord.indexOf("__lp") !== -1) {
            processedWord = processedWord.replace(/lp\d+/g, "");
          }
          if (processedWord.indexOf("__wp") !== -1) {
            processedWord = processedWord.replace(/wp\d+/g, "");
          }

          // TODO: These tasks should update the lyrics with the "onInput" callback
          // TODO 2: The components are still ugly
          if (processedWord.indexOf("__wst") !== -1) {
            return (
              <WordSelectionTaskView
                key={wordIndex}
                line={processedWord}
                song={song}
                onInput={() => {}}
              />
            );
          }
          if (processedWord.indexOf("__lrt") !== -1) {
            return (
              <LineReorderingTaskView
                key={wordIndex}
                line={processedWord}
                song={song}
                onInput={(response: TaskResponse) => {}}
              />
            );
          }

          return (
            <span
              id={`word-${wordIndex}`}
              key={wordIndex}
              className={activeClass}
              onClick={() => onSeek(item.time)}
            >
              {processedWord}{" "}
            </span>
          );
        })}
        {line.length == 0 && <br />}
      </p>
    ));
  };

  return (
    <div>
      <div>{renderLyrics()}</div>

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
