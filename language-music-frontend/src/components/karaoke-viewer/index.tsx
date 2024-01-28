import React, { useState, useEffect } from "react";

type LyricLine = {
  word: string;
  time: number; // in seconds
};

type KaraokeLyricsProps = {
  lyrics: string;
  currentTime: number;
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

const KaraokeLyrics: React.FC<KaraokeLyricsProps> = ({
  lyrics,
  currentTime,
}) => {
  const [parsedLyrics, setParsedLyrics] = useState<LyricLine[][]>([]);

  useEffect(() => {
    setParsedLyrics(parseLrc(lyrics));
  }, [lyrics]);

  const renderLyrics = () => {
    return parsedLyrics.map((line, lineIndex) => (
      <div key={lineIndex}>
        {line.map((item, wordIndex) => {
          const isActive =
            currentTime >= item.time &&
            (!line[wordIndex + 1] || currentTime < line[wordIndex + 1].time) &&
            currentTime <=
              (lineIndex + 1 < parsedLyrics.length &&
              parsedLyrics[lineIndex + 1].length > 0
                ? parsedLyrics[lineIndex + 1][0].time
                : item.time + 3);
          const activeStyle = isActive
            ? { fontWeight: "bold", fontSize: "larger", color: "white" }
            : { color: "white" };

          return (
            <span key={wordIndex} style={activeStyle}>
              {item.word}{" "}
            </span>
          );
        })}
        {line.length == 0 && <br />}
      </div>
    ));
  };

  return <div>{renderLyrics()}</div>;
};

export default KaraokeLyrics;
