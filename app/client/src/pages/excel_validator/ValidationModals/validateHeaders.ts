export const validateHeaders = (
  normalizedHeaders: string[],
  requiredHeaders: string[],
): string[] => {
  return requiredHeaders.filter((header) => !normalizedHeaders.includes(header));
};
