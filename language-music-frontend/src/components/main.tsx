import React from "react";
import TopBar from "@/components/top-bar";
import SongView from "@/components/song-view";
import { Tabs } from "@/components/tabs";

const MainComponent = () => {
  return (
    <div className="flex h-screen overflow-hidden flex-col">
      <TopBar />
      <Tabs>
        <SongView />
        <SongView />
        <SongView />
      </Tabs>
    </div>
  );
};

export default MainComponent;
