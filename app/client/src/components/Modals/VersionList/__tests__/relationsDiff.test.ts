import { describe, it, expect, vi } from "vitest";
import { diffRelations } from "../Utils";

vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("diffRelations", () => {
  const baseDatasetRelation = {
    id: 1,
    relation_kind: "dataset",
    title: "Target Dataset",
    status: "PUBLISHED",
    internal_only: false,
    dataset_id: 42,
    relation_type: "dct:hasVersion",
    previous_version_dataset_id: null,
  };

  const baseExternalRelation = {
    id: 2,
    relation_kind: "external",
    external_url: "https://example.com/resource",
    external_role: "is-referenced-by",
    external_description: "An external reference",
  };

  it("returns empty array when relations are identical", () => {
    expect(diffRelations([baseDatasetRelation], [baseDatasetRelation])).toEqual([]);
  });

  it("detects a new dataset relation", () => {
    const result = diffRelations([], [baseDatasetRelation]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("relations[dataset|dct:hasVersion|42]");
    expect(result[0].oldValue).toBeUndefined();
    expect(result[0].newValue).toEqual(baseDatasetRelation);
  });

  it("detects a deleted dataset relation", () => {
    const result = diffRelations([baseDatasetRelation], []);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("relations[dataset|dct:hasVersion|42]");
    expect(result[0].oldValue).toEqual(baseDatasetRelation);
    expect(result[0].newValue).toBeUndefined();
  });

  it("detects a new external relation", () => {
    const result = diffRelations([], [baseExternalRelation]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("relations[external|https://example.com/resource]");
    expect(result[0].oldValue).toBeUndefined();
    expect(result[0].newValue).toEqual(baseExternalRelation);
  });

  it("detects a deleted external relation", () => {
    const result = diffRelations([baseExternalRelation], []);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("relations[external|https://example.com/resource]");
    expect(result[0].oldValue).toEqual(baseExternalRelation);
    expect(result[0].newValue).toBeUndefined();
  });

  it("detects field-level changes on a dataset relation", () => {
    const updated = { ...baseDatasetRelation, title: "Updated Target" };
    const result = diffRelations([baseDatasetRelation], [updated]);
    expect(result).toEqual([
      {
        path: "relations[dataset|dct:hasVersion|42].title",
        oldValue: "Target Dataset",
        newValue: "Updated Target",
      },
    ]);
  });

  it("detects field-level changes on an external relation", () => {
    const updated = { ...baseExternalRelation, external_description: "Updated description" };
    const result = diffRelations([baseExternalRelation], [updated]);
    expect(result).toEqual([
      {
        path: "relations[external|https://example.com/resource].external_description",
        oldValue: "An external reference",
        newValue: "Updated description",
      },
    ]);
  });

  it("handles multiple relations with mixed changes", () => {
    const relation2 = {
      ...baseDatasetRelation,
      id: 3,
      relation_type: "dct:isPartOf",
      dataset_id: 99,
      title: "Parent Dataset",
    };

    const oldRelations = [baseDatasetRelation, relation2];
    const newRelations = [{ ...baseDatasetRelation, title: "Renamed" }, baseExternalRelation];

    const result = diffRelations(oldRelations, newRelations);

    const updated = result.filter((d) => d.path.includes("[dataset|dct:hasVersion|42]."));
    const deleted = result.filter((d) => d.path === "relations[dataset|dct:isPartOf|99]");
    const added = result.filter(
      (d) => d.path === "relations[external|https://example.com/resource]",
    );

    expect(updated).toHaveLength(1);
    expect(updated[0].newValue).toBe("Renamed");
    expect(deleted).toHaveLength(1);
    expect(deleted[0].newValue).toBeUndefined();
    expect(added).toHaveLength(1);
    expect(added[0].oldValue).toBeUndefined();
  });

  it("handles undefined or empty inputs", () => {
    expect(diffRelations([], [])).toEqual([]);
    expect(diffRelations(undefined, undefined)).toEqual([]);
    expect(diffRelations(undefined, [baseDatasetRelation])).toHaveLength(1);
    expect(diffRelations([baseDatasetRelation], undefined)).toHaveLength(1);
  });

  it("ignores id differences when relation key matches", () => {
    const sameRelationDifferentId = { ...baseDatasetRelation, id: 999 };
    const result = diffRelations([baseDatasetRelation], [sameRelationDifferentId]);
    // Only the id field should differ
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("relations[dataset|dct:hasVersion|42].id");
  });
});
