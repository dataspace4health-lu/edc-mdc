export const getDuplicateStringValue = (
  values: string[] | undefined,
  normalize: (value: string) => string = (value) => value.trim(),
): string | null => {
  if (!values || values.length === 0) {
    return null;
  }

  const seen = new Set<string>();
  for (const value of values) {
    const normalizedValue = normalize(value);
    if (seen.has(normalizedValue)) {
      return value;
    }
    seen.add(normalizedValue);
  }

  return null;
};

export const getDuplicateNumberValue = (values: number[] | undefined): number | null => {
  if (!values || values.length === 0) {
    return null;
  }

  const seen = new Set<number>();
  for (const value of values) {
    if (seen.has(value)) {
      return value;
    }
    seen.add(value);
  }

  return null;
};
