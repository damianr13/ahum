const extractIndex = (line: string, identifier: string): number | undefined => {
  const startOfIndexNumber = line.indexOf(identifier) + identifier.length;
  const endOfIndexNumber = line.indexOf("_", startOfIndexNumber);
  if (startOfIndexNumber === -1 || endOfIndexNumber === -1) return undefined;

  const indexAsString = line.substring(startOfIndexNumber, endOfIndexNumber);
  return parseInt(indexAsString);
};

export { extractIndex };
