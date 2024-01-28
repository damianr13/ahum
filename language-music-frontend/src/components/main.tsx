import { useCallback, useEffect, useMemo, useState } from "react";
import { Song } from "@/models/song";
import backend from "@/services/backend";
import WordSelectionTaskView from "@/components/word-selection-task-view";
import LineReorderingTaskView from "@/components/line-reordering-task-view";
import { TaskResponse } from "@/models/task-response";
import { useSearchParams } from "next/navigation";
import WelcomePage from "@/components/welcome-page";
import KaraokeLyrics from "@/components/karaoke-viewer";
import YouTube from "react-youtube";

const MainComponent = () => {
  const [song, setSong] = useState<Song | undefined>(undefined);
  const [updatedLyrics, setUpdatedLyrics] = useState<string | undefined>();
  const query = useSearchParams();
  const [syncedLyrics, setSyncedLyrics] = useState<string | undefined>();

  const [selectedLanguage, setSelectedLanguage] = useState<
    string | undefined
  >();
  const [currentTime, setCurrentTime] = useState(0);
  const [player, setPlayer] = useState<any>(null);

  const onReady = (event: { target: any }) => {
    // Access to player in all event handlers via event.target
    setPlayer(event.target);
  };

  const onStateChange = (event: { target: any }) => {
    // Update currentTime every second
    if (event.target.getPlayerState() === YouTube.PlayerState.PLAYING) {
      const interval = setInterval(() => {
        setCurrentTime(event.target.getCurrentTime());
      }, 10);
      return () => clearInterval(interval);
    }
  };

  // Load the hardcoded lyrics file from public/lyrics.lrc
  useEffect(() => {
    fetch("/lyrics.lrc")
      .then((response) => response.text())
      .then((lyrics) => {
        setSyncedLyrics(lyrics);
      });
  }, []);

  // Get the language from the query parameters

  useEffect(() => {
    if (!query?.has("language")) return;
    setSelectedLanguage(query.get("language") as string);
  }, [query]);

  useEffect(() => {
    setUpdatedLyrics(song?.processed_lyrics);
  }, [song]);

  useEffect(() => {
    if (!selectedLanguage) return;
    backend.getSong(selectedLanguage).then((song) => {
      setSong(song);
    });
  }, [selectedLanguage]);

  const extractIndex = useCallback(
    (line: string, identifier: string): number | undefined => {
      const startOfIndexNumber = line.indexOf(identifier) + identifier.length;
      const endOfIndexNumber = line.indexOf("_", startOfIndexNumber);
      if (startOfIndexNumber === -1 || endOfIndexNumber === -1)
        return undefined;

      const indexAsString = line.substring(
        startOfIndexNumber,
        endOfIndexNumber,
      );
      return parseInt(indexAsString);
    },
    [],
  );

  const indexesOfLineReplacementTaskLines: number[] = useMemo(() => {
    if (!song) return [];

    return song.processed_lyrics
      .split("\n")
      .map((line, index) => [line, index])
      .filter((pair: (string | number)[]) => {
        const line = pair[0] as string;
        return line.indexOf("_lp") !== -1;
      })
      .map((pair: (string | number)[]) => {
        const lineIndex = pair[1] as number;
        const line = pair[0] as string;
        const taskIndex = extractIndex(line, "lp");
        return [taskIndex, lineIndex] as [number, number];
      })
      .sort((a, b) => a[0] - b[0])
      .map((pair) => pair[1]);
  }, [song, extractIndex]);

  return (
    <>
      <div className="container">
        {!selectedLanguage && <WelcomePage />}
        {song && updatedLyrics && (
          <>
            <div className="embed-container">
              <YouTube
                videoId={song?.youtube_id}
                opts={{
                  style: { marginRight: "1%", marginLeft: "1%" },
                  width: "98%",
                  height: "400px",
                  frameBorder: "0",
                  allow: "autoplay; encrypted-media",
                  title: "video",
                }}
                onReady={onReady}
                onStateChange={onStateChange}
              />
            </div>
            <div className={"lyrics-side-by-side"}>
              <div>
                {updatedLyrics.split("\n").map((line, index) => {
                  if (line.indexOf("lp") !== -1) {
                    line = line.replace(/lp\d+/g, "");
                  }
                  if (line.indexOf("wp") !== -1) {
                    line = line.replace(/wp\d+/g, "");
                  }
                  if (
                    line.indexOf("wst") !== -1 &&
                    song?.word_selection_tasks
                  ) {
                    const wordSelectionTask = song.word_selection_tasks.find(
                      (task) => {
                        return task.task_id === extractIndex(line, "wst");
                      },
                    );
                    if (!wordSelectionTask) return null;
                    return (
                      <WordSelectionTaskView
                        key={index}
                        task={wordSelectionTask}
                        onInput={() => {
                          if (!updatedLyrics) return;
                          const regexp = new RegExp(
                            `_*wp${wordSelectionTask.task_id}_*`,
                            "g",
                          );
                          const newUpdatedLyrics = updatedLyrics.replace(
                            regexp,
                            wordSelectionTask.target_word,
                          );
                          setUpdatedLyrics(newUpdatedLyrics);
                        }}
                      />
                    );
                  }

                  if (
                    line.indexOf("lrt") !== -1 &&
                    song?.line_reordering_tasks
                  ) {
                    const lineReorderingTask = song.line_reordering_tasks.find(
                      (task) => {
                        return task.task_id === extractIndex(line, "lrt");
                      },
                    );
                    if (!lineReorderingTask) return null;
                    return (
                      <LineReorderingTaskView
                        key={index}
                        task={lineReorderingTask}
                        onInput={(response: TaskResponse) => {
                          console.log(
                            "lines",
                            indexesOfLineReplacementTaskLines,
                          );
                          console.log("response", response);
                          if (!updatedLyrics) return;
                          const replacement = response.done
                            ? lineReorderingTask.original_line
                            : response.response +
                              "_".repeat(
                                lineReorderingTask.original_line.split(" ")
                                  .length - response.response.split(" ").length,
                              );
                          const newUpdatedLyrics = updatedLyrics
                            .split("\n")
                            .map((line, index) => {
                              if (
                                indexesOfLineReplacementTaskLines[
                                  lineReorderingTask.task_id
                                ] !== index
                              ) {
                                return line;
                              }
                              return replacement;
                            })
                            .join("\n");
                          console.log(replacement);
                          setUpdatedLyrics(newUpdatedLyrics);
                        }}
                      />
                    );
                  }

                  return (
                    <p key={index} className="lyrics">
                      {line}
                    </p>
                  );
                })}
              </div>
              <div>
                <KaraokeLyrics
                  lyrics={syncedLyrics ?? ""}
                  currentTime={currentTime}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default MainComponent;
