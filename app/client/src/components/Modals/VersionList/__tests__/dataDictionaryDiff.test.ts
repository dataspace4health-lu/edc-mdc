import { describe, it, expect, vi } from "vitest";
import { diffDataDictionaries } from "../Utils";

vi.mock("../../../../zodiosClient/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("diffDataDictionaries", () => {
  const baseEntry = {
    id: 1,
    field_name: "age",
    field_description: "Age of the person",
    data_type: "integer",
    dataset_id: 10,
  };

  it("returns empty array when dictionaries are identical", () => {
    expect(diffDataDictionaries([baseEntry], [baseEntry])).toEqual([]);
  });

  it("detects a new data dictionary entry", () => {
    const result = diffDataDictionaries([], [baseEntry]);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("data_dictionaries[age]");
    expect(result[0].oldValue).toBeUndefined();
    expect(result[0].newValue).toEqual(baseEntry);
  });

  it("detects a deleted data dictionary entry", () => {
    const result = diffDataDictionaries([baseEntry], []);
    expect(result).toHaveLength(1);
    expect(result[0].path).toBe("data_dictionaries[age]");
    expect(result[0].oldValue).toEqual(baseEntry);
    expect(result[0].newValue).toBeUndefined();
  });

  it("detects field-level changes on matched entries", () => {
    const updated = { ...baseEntry, field_description: "Updated description" };
    const result = diffDataDictionaries([baseEntry], [updated]);
    expect(result).toEqual([
      {
        path: "data_dictionaries[age].field_description",
        oldValue: "Age of the person",
        newValue: "Updated description",
      },
    ]);
  });

  it("handles multiple entries with mixed changes", () => {
    const entry1 = { ...baseEntry, field_name: "age" };
    const entry2 = { ...baseEntry, field_name: "name", data_type: "string" };
    const entry3 = { ...baseEntry, field_name: "email", data_type: "string" };

    const oldDicts = [entry1, entry2];
    const newDicts = [{ ...entry1, field_description: "changed" }, entry3];

    const result = diffDataDictionaries(oldDicts, newDicts);

    const updated = result.filter((d) => d.path.includes("[age]."));
    const deleted = result.filter((d) => d.path === "data_dictionaries[name]");
    const added = result.filter((d) => d.path === "data_dictionaries[email]");

    expect(updated).toHaveLength(1);
    expect(updated[0].newValue).toBe("changed");
    expect(deleted).toHaveLength(1);
    expect(deleted[0].newValue).toBeUndefined();
    expect(added).toHaveLength(1);
    expect(added[0].oldValue).toBeUndefined();
  });

  it("handles undefined or empty inputs", () => {
    expect(diffDataDictionaries([], [])).toEqual([]);
    expect(diffDataDictionaries(undefined, undefined)).toEqual([]);
    expect(diffDataDictionaries(undefined, [baseEntry])).toHaveLength(1);
    expect(diffDataDictionaries([baseEntry], undefined)).toHaveLength(1);
  });

  it("detects a new field added to an existing entry", () => {
    const withExtra = { ...baseEntry, variable_unit: "kg" };
    const result = diffDataDictionaries([baseEntry], [withExtra]);
    const sensDiff = result.find((d) => d.path.endsWith(".variable_unit"));
    expect(sensDiff).toBeDefined();
    expect(sensDiff?.oldValue).toBeUndefined();
    expect(sensDiff?.newValue).toBe("kg");
  });

  it("detects a field removed from an existing entry", () => {
    const { field_description, ...withoutDesc } = baseEntry;
    const result = diffDataDictionaries([baseEntry], [withoutDesc]);
    const descDiff = result.find((d) => d.path.endsWith(".field_description"));
    expect(descDiff).toBeDefined();
    expect(descDiff?.oldValue).toBe("Age of the person");
    expect(descDiff?.newValue).toBeUndefined();
  });
});
