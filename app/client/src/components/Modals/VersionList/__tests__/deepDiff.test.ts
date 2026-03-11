import { deepDiff } from "../Utils";
import { describe, it, expect, vi } from "vitest";

// Mock the client
vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("deepDiff", () => {
  it("returns empty array if objects are equal", () => {
    const obj1 = { a: 1, b: "test", c: { d: 2 } };
    const obj2 = { a: 1, b: "test", c: { d: 2 } };

    expect(deepDiff(obj1, obj2)).toEqual([]);
  });

  it("detects primitive value differences", () => {
    const obj1 = { a: 1 };
    const obj2 = { a: 2 };

    expect(deepDiff(obj1, obj2)).toEqual([{ path: "a", oldValue: 1, newValue: 2 }]);
  });

  it("detects nested object differences", () => {
    const obj1 = { a: { b: 1 } };
    const obj2 = { a: { b: 2 } };

    expect(deepDiff(obj1, obj2)).toEqual([{ path: "a.b", oldValue: 1, newValue: 2 }]);
  });

  it("detects array differences", () => {
    const obj1 = { arr: [1, 2, 3] };
    const obj2 = { arr: [1, 2, 4] };

    expect(deepDiff(obj1, obj2)).toEqual([
      { path: "arr", oldValue: [1, 2, 3], newValue: [1, 2, 4] },
    ]);
  });

  it("detects added or removed keys", () => {
    const obj1 = { a: 1 };
    const obj2 = { a: 1, b: 2 };

    expect(deepDiff(obj1, obj2)).toEqual([{ path: "b", oldValue: undefined, newValue: 2 }]);
  });

  it("handles null and undefined values", () => {
    const obj1 = { a: null, b: undefined };
    const obj2 = { a: 1, b: undefined };

    expect(deepDiff(obj1, obj2)).toEqual([{ path: "a", oldValue: null, newValue: 1 }]);
  });

  it("does not detect difference for arrays of objects with same content in different order", () => {
    const obj1 = {
      languages: [
        {
          value: "http://publications.europa.eu/resource/authority/language/LTZ",
          eng_label: "Luxembourgish",
        },
        {
          value: "http://publications.europa.eu/resource/authority/language/FRA",
          eng_label: "French",
        },
      ],
    };
    const obj2 = {
      languages: [
        {
          value: "http://publications.europa.eu/resource/authority/language/FRA",
          eng_label: "French",
        },
        {
          value: "http://publications.europa.eu/resource/authority/language/LTZ",
          eng_label: "Luxembourgish",
        },
      ],
    };

    expect(deepDiff(obj1, obj2)).toEqual([]);
  });

  it("detects difference when arrays of objects have different content", () => {
    const obj1 = {
      languages: [
        {
          value: "http://publications.europa.eu/resource/authority/language/LTZ",
          eng_label: "Luxembourgish",
        },
      ],
    };
    const obj2 = {
      languages: [
        {
          value: "http://publications.europa.eu/resource/authority/language/FRA",
          eng_label: "French",
        },
      ],
    };

    expect(deepDiff(obj1, obj2)).toEqual([
      {
        path: "languages",
        oldValue: obj1.languages,
        newValue: obj2.languages,
      },
    ]);
  });
});
