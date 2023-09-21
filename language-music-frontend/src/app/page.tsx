"use client";

import {useEffect, useMemo, useState} from "react";
import backend from "@/services/backend";
import {Song} from "@/models/song";

export default function Home() {
  const [embedController, setEmbedController] = useState<any>(undefined);

  const [song, setSong] = useState<Song | undefined>(undefined)

  const songId = useMemo(() => {
    if (!song) return undefined;
    return song.spotify_id
  }, [song]);


  useEffect(() => {
    backend.getSong("de").then((song) => {
      setSong(song)
    })
  }, [])

  useEffect(() => {
    if (!songId) return;

    const script = document.createElement('script');
    script.src = "https://open.spotify.com/embed-podcast/iframe-api/v1";
    script.async = true;

    document.body.appendChild(script);

    window.onSpotifyIframeApiReady = (iFrameAPI: any) => {
      console.log("iFrameAPI", iFrameAPI)
      let element = document.getElementById('embed-iframe');
      let options = {
          uri: `spotify:track:${songId}`
        };
      let callback = (EmbedController: any) => {
        console.log("EmbedController", EmbedController);
        setEmbedController(EmbedController)
      };
      iFrameAPI.createController(element, options, callback);
    };

  }, [songId]);

  return (
    <>
      <div className="container">
        <div className="main-wrapper" id={"embed-iframe"}>
        </div>
        <br/>
        <button onClick={() => {
          embedController?.togglePlay();
        }}>Pause
        </button>
        {song && (
          <>
                  <div dangerouslySetInnerHTML={{ __html: song.lyrics }} />

          </>
        )}
      </div>
    </>
  )
}
