import { describe, it, expect } from "vitest";
import { getFieldErrors } from "./formFieldErrors";

describe("getFieldErrors", () => {
  it("returns undefined when no errors exist for a field", () => {
    const result = getFieldErrors({ otherField: ["Required"] }, "title");
    expect(result).toBeUndefined();
  });

  it("returns errors for exact field key", () => {
    const result = getFieldErrors({ title: ["Required"] }, "title");
    expect(result).toEqual(["Required"]);
  });

  it("includes nested and indexed field errors", () => {
    const result = getFieldErrors(
      {
        conformsTo: ["Invalid value"],
        "conformsTo[0]": ["Must be a valid URL"],
        "conformsTo[1]": ["Must be a valid URL"],
        "conformsTo.extra": ["Another error"],
      },
      "conformsTo",
    );

    expect(result).toEqual(["Invalid value", "Must be a valid URL", "Another error"]);
  });

  it("deduplicates repeated messages and ignores null entries", () => {
    const result = getFieldErrors(
      {
        accessURLs: ["Invalid URL"],
        "accessURLs[0]": ["Invalid URL"],
        "accessURLs[1]": null,
      },
      "accessURLs",
    );

    expect(result).toEqual(["Invalid URL"]);
  });

  it("returns undefined for null or undefined form errors", () => {
    expect(getFieldErrors(null, "title")).toBeUndefined();
    expect(getFieldErrors(undefined, "title")).toBeUndefined();
  });
});
