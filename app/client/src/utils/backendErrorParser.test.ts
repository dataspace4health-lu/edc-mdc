import { describe, it, expect } from "vitest";
import { snakeToCamel, parseBackendErrors } from "./backendErrorParser";

describe("backendErrorParser", () => {
  describe("snakeToCamel", () => {
    it("should convert snake_case to camelCase", () => {
      expect(snakeToCamel("temporal_resolution")).toBe("temporalResolution");
      expect(snakeToCamel("user_name")).toBe("userName");
      expect(snakeToCamel("dataset_type")).toBe("datasetType");
    });

    it("should handle strings with multiple underscores", () => {
      expect(snakeToCamel("very_long_field_name")).toBe("veryLongFieldName");
      expect(snakeToCamel("a_b_c_d")).toBe("aBCD");
    });

    it("should handle strings without underscores", () => {
      expect(snakeToCamel("alreadycamelcase")).toBe("alreadycamelcase");
      expect(snakeToCamel("title")).toBe("title");
    });

    it("should handle empty string", () => {
      expect(snakeToCamel("")).toBe("");
    });
  });

  describe("parseBackendErrors", () => {
    it("should parse single field error correctly", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              type: "value_error",
              loc: ["body", "temporal_resolution"],
              msg: "Value error, Temporal resolution must be in ISO 8601 format",
              input: "-10",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        temporalResolution: ["Value error, Temporal resolution must be in ISO 8601 format"],
      });
    });

    it("should parse multiple field errors correctly", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              loc: ["body", "temporal_resolution"],
              msg: "Invalid temporal resolution",
            },
            {
              loc: ["body", "spatial_resolutions"],
              msg: "Must be a positive number",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        temporalResolution: ["Invalid temporal resolution"],
        spatialResolutions: ["Must be a positive number"],
      });
    });

    it("should handle multiple errors for the same field", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              loc: ["body", "title"],
              msg: "Title is required",
            },
            {
              loc: ["body", "title"],
              msg: "Title must be at least 3 characters",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        title: ["Title is required", "Title must be at least 3 characters"],
      });
    });

    it("should handle nested field errors (e.g., distributions)", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              loc: ["body", "distributions", 0, "temporal_resolution"],
              msg: "Invalid duration format",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        "distributions.0.temporalResolution": ["Invalid duration format"],
      });
    });

    it("should handle array index in error path", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              loc: ["body", "distributions", 0, "title"],
              msg: "Distribution title is required",
            },
            {
              loc: ["body", "distributions", 1, "access_urls"],
              msg: "At least one access URL is required",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        "distributions.0.title": ["Distribution title is required"],
        "distributions.1.accessUrls": ["At least one access URL is required"],
      });
    });

    it("should return empty object for missing detail array", () => {
      const errorResponse = {
        data: {},
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({});
    });

    it("should return empty object for null/undefined response", () => {
      expect(parseBackendErrors(null)).toEqual({});
      expect(parseBackendErrors(undefined)).toEqual({});
      expect(parseBackendErrors({})).toEqual({});
    });

    it("should return empty object for non-array detail", () => {
      const errorResponse = {
        data: {
          detail: "Not an array",
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({});
    });

    it("should skip errors without loc property", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              msg: "Error without location",
            },
            {
              loc: ["body", "title"],
              msg: "Valid error",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        title: ["Valid error"],
      });
    });

    it("should skip errors with empty loc array", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              loc: [],
              msg: "Error with empty loc",
            },
            {
              loc: ["body"],
              msg: "Error with only body in loc",
            },
            {
              loc: ["body", "title"],
              msg: "Valid error",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        title: ["Valid error"],
      });
    });

    it("should use default message when msg is missing", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              loc: ["body", "title"],
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        title: ["Validation error"],
      });
    });

    it("should handle complex nested structures", () => {
      const errorResponse = {
        data: {
          detail: [
            {
              loc: ["body", "distributions", 0, "policy_actions", 0, "temporal_restriction_start"],
              msg: "Invalid date format",
            },
          ],
        },
      };

      const result = parseBackendErrors(errorResponse);

      expect(result).toEqual({
        "distributions.0.policyActions.0.temporalRestrictionStart": ["Invalid date format"],
      });
    });
  });
});
