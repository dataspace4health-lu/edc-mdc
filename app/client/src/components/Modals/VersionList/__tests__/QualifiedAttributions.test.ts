import { describe, it, expect, vi } from "vitest";
import { diffQualifiedAttributions } from "../Utils";

vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("diffQualifiedAttributions", () => {
  const baseQualifiedAttribution = {
    id: 1,
    dataset_id: 1,
    organisation_id: 5,
    organisation_name: "Data Luxembourg",
    role: "Data Curator",
  };

  it("returns empty array when qualified attributions are identical", () => {
    expect(
      diffQualifiedAttributions([baseQualifiedAttribution], [baseQualifiedAttribution]),
    ).toEqual([]);
  });

  it("detects a new qualified attribution", () => {
    const result = diffQualifiedAttributions([], [baseQualifiedAttribution]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("qualified_attributions[5|Data Curator]");
    expect(result[0].oldValue).toBeUndefined();
    expect(result[0].newValue).toEqual(baseQualifiedAttribution);
  });

  it("detects a deleted qualified attribution", () => {
    const result = diffQualifiedAttributions([baseQualifiedAttribution], []);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("qualified_attributions[5|Data Curator]");
    expect(result[0].oldValue).toEqual(baseQualifiedAttribution);
    expect(result[0].newValue).toBeUndefined();
  });

  it("detects field-level changes on a qualified attribution", () => {
    const updated = { ...baseQualifiedAttribution, organisation_name: "Luxembourg Data Office" };
    const result = diffQualifiedAttributions([baseQualifiedAttribution], [updated]);
    expect(result).toEqual([
      {
        path: "qualified_attributions[5|Data Curator].organisation_name",
        oldValue: "Data Luxembourg",
        newValue: "Luxembourg Data Office",
      },
    ]);
  });

  it("handles multiple qualified attributions with mixed changes", () => {
    const qa2 = {
      ...baseQualifiedAttribution,
      id: 3,
      organisation_id: 3,
      organisation_name: "CTIE",
      role: "Contributor",
    };

    const oldQAs = [baseQualifiedAttribution, qa2];
    const newQAs = [
      { ...baseQualifiedAttribution, organisation_name: "Renamed Org" },
      {
        id: 7,
        dataset_id: 1,
        organisation_id: 7,
        organisation_name: "STATEC",
        role: "Publisher",
      },
    ];

    const result = diffQualifiedAttributions(oldQAs, newQAs);

    const updated = result.filter((d) => d.path.includes("[5|Data Curator]."));
    const deleted = result.filter((d) => d.path === "qualified_attributions[3|Contributor]");
    const added = result.filter((d) => d.path === "qualified_attributions[7|Publisher]");

    expect(updated).toHaveLength(1);
    expect(updated[0].newValue).toBe("Renamed Org");
    expect(deleted).toHaveLength(1);
    expect(deleted[0].newValue).toBeUndefined();
    expect(added).toHaveLength(1);
    expect(added[0].oldValue).toBeUndefined();
  });

  it("handles undefined or empty inputs", () => {
    expect(diffQualifiedAttributions([], [])).toEqual([]);
    expect(diffQualifiedAttributions(undefined, undefined)).toEqual([]);
    expect(diffQualifiedAttributions(undefined, [baseQualifiedAttribution])).toHaveLength(1);
    expect(diffQualifiedAttributions([baseQualifiedAttribution], undefined)).toHaveLength(1);
  });

  it("ignores id differences when qualified attribution key matches", () => {
    const sameQADifferentId = { ...baseQualifiedAttribution, id: 999 };
    const result = diffQualifiedAttributions([baseQualifiedAttribution], [sameQADifferentId]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("qualified_attributions[5|Data Curator].id");
  });
});
