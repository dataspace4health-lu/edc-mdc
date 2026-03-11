import { describe, it, expect, vi } from "vitest";
import { diffDistributions } from "../Utils";

// Mock the client
vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("diffDistributions", () => {
  const baseDist = {
    id: 1,
    title: "Dist A",
    description: "desc",
    dataset_id: 10,
    access_url: "https://example.com",
    rights_statement: "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC",
  };

  it("returns empty array when distributions are identical", () => {
    expect(diffDistributions([baseDist], [baseDist])).toEqual([]);
  });

  it("detects a new distribution", () => {
    const result = diffDistributions([], [baseDist]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("distributions[Dist A||desc||https://example.com]");
    expect(result[0].oldValue).toBeUndefined();
    expect(result[0].newValue).toEqual(baseDist);
  });

  it("detects a deleted distribution", () => {
    const result = diffDistributions([baseDist], []);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("distributions[Dist A||desc||https://example.com]");
    expect(result[0].oldValue).toEqual(baseDist);
    expect(result[0].newValue).toBeUndefined();
  });

  it("detects field-level changes on matched distributions (same key)", () => {
    const updated = { ...baseDist, rights_statement: "changed" };
    const result = diffDistributions([baseDist], [updated]);
    expect(result).toEqual([
      {
        path: "distributions[Dist A||desc||https://example.com].rights_statement",
        oldValue: "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC",
        newValue: "changed",
      },
    ]);
  });

  it("treats changed description as delete + add (different key)", () => {
    const updated = { ...baseDist, description: "new desc" };
    const result = diffDistributions([baseDist], [updated]);
    expect(result).toHaveLength(2);
    const deleted = result.find((d) => d.oldValue && !d.newValue);
    const added = result.find((d) => !d.oldValue && d.newValue);
    expect(deleted?.path).toBe("distributions[Dist A||desc||https://example.com]");
    expect(added?.path).toBe("distributions[Dist A||new desc||https://example.com]");
  });

  it("treats changed title as delete + add (different key)", () => {
    const renamed = { ...baseDist, title: "Dist B" };
    const result = diffDistributions([baseDist], [renamed]);
    expect(result).toHaveLength(2);
    const deleted = result.find((d) => d.oldValue && !d.newValue);
    const added = result.find((d) => !d.oldValue && d.newValue);
    expect(deleted?.path).toBe("distributions[Dist A||desc||https://example.com]");
    expect(added?.path).toBe("distributions[Dist B||desc||https://example.com]");
  });

  it("handles multiple distributions with mixed changes", () => {
    const dist1 = { ...baseDist, description: "d1", access_url: "http://a" };
    const dist2 = { ...baseDist, description: "d2", access_url: "http://b" };
    const dist3 = { ...baseDist, description: "d3", access_url: "http://c" };

    const oldDists = [dist1, dist2];
    const newDists = [{ ...dist1, rights_statement: "changed" }, dist3];

    const result = diffDistributions(oldDists, newDists);

    const updated = result.filter((d) => d.path.includes("[Dist A||d1||http://a]."));
    const deleted = result.filter((d) => d.path === "distributions[Dist A||d2||http://b]");
    const added = result.filter((d) => d.path === "distributions[Dist A||d3||http://c]");

    expect(updated).toHaveLength(1);
    expect(updated[0].newValue).toBe("changed");
    expect(deleted).toHaveLength(1);
    expect(deleted[0].newValue).toBeUndefined();
    expect(added).toHaveLength(1);
    expect(added[0].oldValue).toBeUndefined();
  });

  it("handles undefined or empty inputs", () => {
    expect(diffDistributions([], [])).toEqual([]);
    expect(diffDistributions(undefined, undefined)).toEqual([]);
    expect(diffDistributions(undefined, [baseDist])).toHaveLength(1);
    expect(diffDistributions([baseDist], undefined)).toHaveLength(1);
  });

  it("handles distributions without title", () => {
    const noTitle = { id: 5, description: "no title dist", dataset_id: 10 };
    const result = diffDistributions([], [noTitle]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("distributions[||no title dist||]");
  });

  it("handles distributions with only required fields filled", () => {
    const minimal = { id: 1, dataset_id: 10, access_url: "https://example.com" };
    const result = diffDistributions([], [minimal]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("distributions[||||https://example.com]");
    expect(result[0].newValue).toEqual(minimal);
  });
});
