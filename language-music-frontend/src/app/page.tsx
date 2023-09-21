"use client";

import Image from 'next/image'
import {useEffect, useMemo, useState} from "react";

export default function Home() {
  const [embedController, setEmbedController] = useState<any>(undefined);

  const [songName, setSongName] = useState<string>("")

  const songId = useMemo(() => "1twCDBPDERLBAYFhGjmNfI", [])

  useEffect(() => {
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
      </div>
    </>
  )
}