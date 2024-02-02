import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Song } from "@/models/song";
import backend from "@/services/backend";
import { useSearchParams } from "next/navigation";
import WelcomePage from "@/components/welcome-page";
import KaraokeLyrics from "@/components/karaoke-viewer";
import MusicPlayer from "@/components/music-player";
import TopBar from "@/components/top-bar";

const MainComponent = () => {
  const [song, setSong] = useState<Song | undefined>(undefined);
  const [updatedLyrics, setUpdatedLyrics] = useState<string | undefined>();
  const query = useSearchParams();
  const [syncedLyrics, setSyncedLyrics] = useState<string | undefined>();
  const [isPlayerTop, setIsPlayerTop] = useState(false);
  const [startPlayerAt, setStartPlayerAt] = useState<number | undefined>(
    undefined,
  );

  const [selectedLanguage, setSelectedLanguage] = useState<string | undefined>(
    "sv",
  );
  const [currentTime, setCurrentTime] = useState(0);

  // Opacity variables to animate the transition of the player from top to bottom and vice versa
  const [opacity, setOpacity] = useState("opacity-100 translate-y-0");
  const [translation, setTranslation] = useState("translate-y-0");

  // Toggle the flex direction with intermediate opacity transition
  const toggleFlexDirection = () => {
    setOpacity("opacity-50"); // Step 1: Transition to opacity-50
    setTranslation("translate-y-2");
    setTimeout(() => {
      setTranslation("translate-y-0"); // Step 2: Transition back to translate-y-0")
      setOpacity("opacity-100"); // Step 3: Transition back to opacity-100
    }, 250); // Adjust the timing based on your transition duration
  };

  useEffect(() => {
    toggleFlexDirection();
  }, [isPlayerTop]);

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

  return (
    <div className="flex h-screen overflow-hidden flex-col">
      <TopBar />
      <div
        className={
          "flex h-screen overflow-hidden " +
          (isPlayerTop ? "flex-col" : "flex-col-reverse")
        }
      >
        <div
          className={`transition-all duration-250 ease-in-out ${translation}`}
        >
          {song && (
            <MusicPlayer
              videoId={song.youtube_id}
              isTop={isPlayerTop}
              onSwitchPosition={() => setIsPlayerTop(!isPlayerTop)}
              onPlayerTimeChanged={(time) => setCurrentTime(time)}
              startAt={startPlayerAt}
            />
          )}
        </div>
        <div
          className={`overflow-y-auto transform transition duration-500 ease-in-out ${opacity}`}
        >
          <div className="flex flex-col max-w-[800px] mx-auto">
            {!selectedLanguage && <WelcomePage />}
            {song && updatedLyrics && (
              <>
                <div className="flex flex-row justify-center font-roboto-mono bg-gray-700 text-white p-6 items-center">
                  <KaraokeLyrics
                    lyrics={syncedLyrics ?? ""}
                    currentTime={currentTime}
                    onSeek={(time) => setStartPlayerAt(time)}
                    lyricsUrl={song.lyrics_url}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainComponent;
