import React from "react";
import TopBar from "@/components/top-bar";
import SongView from "@/components/song-view";
import { Tabs } from "@/components/tabs";
import VocabularyView from "@/components/vocabulary-view/";

const MainComponent = () => {
  return (
    <div className="flex h-screen overflow-y-hidden flex-col font-roboto-mono ">
      <TopBar />
      <Tabs>
        <SongView />
        <VocabularyView />
        <VocabularyView />
      </Tabs>
    </div>
  );
};

export default MainComponent;
