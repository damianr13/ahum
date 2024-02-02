import React, { useEffect, useMemo, useState } from "react";
import PlayerButton from "@/components/music-player/player-button";
import YouTube from "react-youtube";

interface MusicPlayerProps {
  videoId: string;
  onSwitchPosition: () => void;
  isTop: boolean;
  onPlayerTimeChanged: (time: number) => void;
  startAt?: number;
}

// Music Player Component

const MusicPlayer = (props: MusicPlayerProps) => {
  const { isTop, onSwitchPosition, videoId, onPlayerTimeChanged, startAt } =
    props;
  const [isPaused, setIsPaused] = useState(true);
  const containerClassNames = useMemo(() => {
    const common =
      "transition-all duration-1000 ease-in-out flex flex-shrink-0 flex-grow-0 w-full";
    const specific = isTop
      ? "flex-col h-[300px] bg-gray-400 p-2 items-center gap-2 md:h-[500px] md:gap-4"
      : "flex-row justify-self-end bg-gray-400 p-3 flex justify-around";

    return `${common} ${specific}`;
  }, [isTop]);

  const frameClassNames = useMemo(() => {
    return isTop ? "flex flex-grow md:w-[800px] w-full" : "w-[200px]";
  }, [isTop]);
  const [player, setPlayer] = useState<any>(null);

  useEffect(() => {
    if (!player) {
      return;
    }

    if (startAt !== undefined) {
      player.seekTo(startAt);
    }
  }, [startAt, player]);

  const onReady = (event: { target: any }) => {
    // Access to player in all event handlers via event.target
    setPlayer(event.target);
  };

  const onStateChange = (event: { target: any }) => {
    // Update currentTime every second
    if (event.target.getPlayerState() === YouTube.PlayerState.PLAYING) {
      if (isPaused) {
        setIsPaused(false);
      }
      const interval = setInterval(() => {
        onPlayerTimeChanged(event.target.getCurrentTime());
      }, 10);
      return () => clearInterval(interval);
    }
  };

  return (
    <div className={containerClassNames}>
      {/* YouTube Iframe */}
      <YouTube
        className={frameClassNames}
        videoId={videoId}
        opts={{
          style: { marginRight: "1%", marginLeft: "1%" },
          width: "98%",
          height: "100%",
          frameBorder: "0",
          allow: "autoplay; encrypted-media",
          title: "video",
        }}
        onReady={onReady}
        onStateChange={onStateChange}
      />

      {/* Playback Control Buttons */}
      <div className="flex items-center space-x-4">
        <PlayerButton
          onClick={() => {
            if (isPaused) {
              player.playVideo();
            } else {
              player.pauseVideo();
            }

            setIsPaused(!isPaused);
          }}
        >
          {isPaused ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z"
              />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15.75 5.25v13.5m-7.5-13.5v13.5"
              />
            </svg>
          )}
        </PlayerButton>
        <PlayerButton onClick={onSwitchPosition}>
          {isTop ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m4.5 5.25 7.5 7.5 7.5-7.5m-15 6 7.5 7.5 7.5-7.5"
              />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m4.5 18.75 7.5-7.5 7.5 7.5"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m4.5 12.75 7.5-7.5 7.5 7.5"
              />
            </svg>
          )}
        </PlayerButton>
      </div>
    </div>
  );
};

export default MusicPlayer;
