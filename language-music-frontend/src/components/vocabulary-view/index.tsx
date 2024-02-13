import { useCallback, useEffect, useState } from "react";
import {
  CEFR_LEVEL_KEY,
  PART_OF_SPEECH_KEY,
  Vocabulary,
  VocabularyFilter,
} from "@/components/vocabulary-view/types";
import VocabularyCard from "./card";
import FilterPanel from "@/components/vocabulary-view/filter-panel";
import { cefrLevelToStringRepr } from "@/components/vocabulary-view/utils";

const VocabularyView = () => {
  const [vocabulary, setVocabulary] = useState<Vocabulary>();
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredVocabulary, setFilteredVocabulary] = useState<Vocabulary>();
  const [vocabularyFilter, setVocabularyFilter] = useState<
    VocabularyFilter | undefined
  >(undefined);

  useEffect(() => {
    if (!vocabulary || !vocabularyFilter) return;

    let newVocabulary = Object.keys(vocabulary)
      .filter((k) => k.startsWith(searchTerm))
      .reduce((acc, key) => {
        if (key in vocabulary) {
          acc[key] = vocabulary[key];
        }
        return acc;
      }, {} as Vocabulary);
    console.log("After search: ", newVocabulary);

    if (
      PART_OF_SPEECH_KEY in vocabularyFilter &&
      vocabularyFilter[PART_OF_SPEECH_KEY].size > 0
    ) {
      newVocabulary = Object.keys(newVocabulary)
        .filter((k) =>
          vocabularyFilter[PART_OF_SPEECH_KEY].has(
            vocabulary[k].part_of_speech,
          ),
        )
        .reduce((acc, key) => {
          if (key in newVocabulary) {
            acc[key] = newVocabulary[key];
          }
          return acc;
        }, {} as Vocabulary);
    }
    console.log("After part of speech:", newVocabulary);

    if (
      CEFR_LEVEL_KEY in vocabularyFilter &&
      vocabularyFilter[CEFR_LEVEL_KEY].size > 0
    ) {
      newVocabulary = Object.keys(newVocabulary)
        .filter((k) =>
          vocabularyFilter[CEFR_LEVEL_KEY].has(
            cefrLevelToStringRepr(vocabulary[k].cefr),
          ),
        )
        .reduce((acc, key) => {
          if (key in newVocabulary) {
            acc[key] = newVocabulary[key];
          }
          return acc;
        }, {} as Vocabulary);
    }
    console.log("After cefr:", newVocabulary);

    setFilteredVocabulary(newVocabulary);
  }, [searchTerm, vocabularyFilter, vocabulary]);

  useEffect(() => {
    fetch("/vocabulary.json")
      .then((response) => response.json())
      .then((s) => setVocabulary(s as Vocabulary));
  }, []);

  const onFilterChange = useCallback((filter: VocabularyFilter) => {
    console.log("Set vocabulary filter");
    setVocabularyFilter(filter);
  }, []);

  return (
    <div
      className={
        "flex flex-col h-full overflow-y-scroll  max-w-screen-sm bg-gray-700 items-center"
      }
    >
      <div className="flex flex-row gap-4 mt-8 mb-6 items-center">
        <div className="rounded-lg flex flex-row p-2 bg-gray-600 shadow-lg gap-2 text-white">
          <input
            className="bg-transparent focus:outline-none"
            onChange={(e) => setSearchTerm(e.currentTarget.value)}
          />
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            className="w-6 h-6 stroke-gray-200"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="m15.75 15.75-2.489-2.489m0 0a3.375 3.375 0 1 0-4.773-4.773 3.375 3.375 0 0 0 4.774 4.774ZM21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
            />
          </svg>
        </div>
        <FilterPanel onFilterChange={onFilterChange} />
      </div>

      {filteredVocabulary &&
        Object.keys(filteredVocabulary)
          .sort(
            (a, b) =>
              (filteredVocabulary[b].wpm ?? 0) -
              (filteredVocabulary[a].wpm ?? 0),
          )
          .map((word, index) => (
            <VocabularyCard
              key={index}
              word={word}
              vocabularyEntry={filteredVocabulary[word]}
            />
          ))}
    </div>
  );
};

export default VocabularyView;
