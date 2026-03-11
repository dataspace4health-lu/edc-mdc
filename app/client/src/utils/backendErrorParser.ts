export const snakeToCamel = (str: string): string => {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const parseBackendErrors = (errorResponse: any): Record<string, string[]> => {
  const errors: Record<string, string[]> = {};

  // Check if the error response has the expected structure
  if (!errorResponse?.data?.detail || !Array.isArray(errorResponse.data.detail)) {
    return errors;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  errorResponse.data.detail.forEach((error: any) => {
    if (!error.loc || !Array.isArray(error.loc)) {
      return;
    }

    // loc is like ["body", "temporal_resolution"] or ["body", "distributions", 0, "temporal_resolution"]
    // We want to remove "body" and convert the rest to camelCase
    const fieldPath = error.loc.slice(1); // Remove "body"

    if (fieldPath.length === 0) {
      return;
    }

    // Convert each part of the path to camelCase and join with dots
    // e.g., ["temporal_resolution"] -> "temporalResolution"
    // e.g., ["distributions", 0, "temporal_resolution"] -> "distributions.0.temporalResolution"
    const fieldName = fieldPath
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .map((part: any) => {
        // If it's a number (array index), keep it as is
        if (typeof part === "number") {
          return part.toString();
        }
        // Otherwise convert snake_case to camelCase
        return snakeToCamel(String(part));
      })
      .join(".");

    // Initialize the array if it doesn't exist
    if (!errors[fieldName]) {
      errors[fieldName] = [];
    }

    // Add the error message
    const message = error.msg || "Validation error";
    errors[fieldName].push(message);
  });

  return errors;
};
