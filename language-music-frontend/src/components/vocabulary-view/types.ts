const CEFR_LEVEL_KEY = "cefr";
const PART_OF_SPEECH_KEY = "part_of_speech";

interface VocabularyDefinition {
  text: string;
  examples: string[];
}

interface VocabularyOption {
  part_of_speech: string;
  definitions: VocabularyDefinition[];
  audio?: string;
}

interface VocabularyEntry {
  success: boolean;
  options: VocabularyOption[];
  base?: string;
  url?: string;
  wpm?: number;
  cefr?: number;
  part_of_speech: string;
}

interface Vocabulary {
  [key: string]: VocabularyEntry;
}

interface VocabularyFilter {
  [key: string]: Set<string>;
}

export type {
  Vocabulary,
  VocabularyDefinition,
  VocabularyOption,
  VocabularyEntry,
  VocabularyFilter,
};

export { CEFR_LEVEL_KEY, PART_OF_SPEECH_KEY };
