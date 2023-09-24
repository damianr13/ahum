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
        <div className="embed-container">
          <iframe src={`https://www.youtube.com/embed/${song?.youtube_id}`}
                  style={{marginRight: "1%", marginLeft: "1%"}}
                  width="98%"
                  height="400px"
                  frameBorder='0'
                  allow='autoplay; encrypted-media'
                  title='video'
          />
        </div>
        <br/>
        {song && (
          <>
            <p className="lyrics">
                {song.processed_lyrics}
            </p>
          </>
        )}
      </div>
    </>
  )
}
