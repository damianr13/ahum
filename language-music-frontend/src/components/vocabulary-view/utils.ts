const levels = ["A1", "A2", "B1", "B2", "C1", "C2"];

const cefrLevelToStringRepr = (cefr?: number | string): string => {
  if (cefr === undefined || typeof cefr === "string") {
    return "??";
  }
  const safeLevel = cefr as number;

  return levels[safeLevel - 1];
};

export { cefrLevelToStringRepr };
