import { describe, it, expect } from "vitest";
import {
  filterFormFieldsByOrganisation,
  sortFormFieldsByLabel,
} from "./filterFormFieldsByOrganisation";
import { ResourceUserType } from "../types";

describe("filterFormFieldsByOrganisation", () => {
  const globalField = {
    value: "global-field",
    eng_label: "Global Field",
    organisation_ids: [],
  };

  const org1Field = {
    value: "org1-field",
    eng_label: "Org 1 Field",
    organisation_ids: [1],
  };

  const org2Field = {
    value: "org2-field",
    eng_label: "Org 2 Field",
    organisation_ids: [2],
  };

  const multiOrgField = {
    value: "multi-org-field",
    eng_label: "Multi Org Field",
    organisation_ids: [1, 3],
  };

  const nullOrgField = {
    value: "null-org-field",
    eng_label: "Null Org Field",
    organisation_ids: null,
  };

  const allFields = [globalField, org1Field, org2Field, multiOrgField, nullOrgField];

  describe("Global access users (roles:manage)", () => {
    const userWithRolesManage = {
      id: 1,
      username: "admin",
      email: "admin@example.com",
      permissions: ["roles:manage"],
      current_organisation: { id: 1, name: "Org 1" },
      feature_options: {
        enable_multi_tenants: true,
      },
    } as unknown as ResourceUserType;

    it("should show all fields when no publisher is selected", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: userWithRolesManage,
        selectedPublisherId: null,
      });

      expect(result).toHaveLength(5);
      expect(result).toContainEqual(globalField);
      expect(result).toContainEqual(org1Field);
      expect(result).toContainEqual(org2Field);
      expect(result).toContainEqual(multiOrgField);
      expect(result).toContainEqual(nullOrgField);
    });

    it("should filter by selected publisher ID", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: userWithRolesManage,
        selectedPublisherId: "2",
      });

      expect(result).toHaveLength(3);
      expect(result).toContainEqual(globalField);
      expect(result).toContainEqual(nullOrgField);
      expect(result).toContainEqual(org2Field);
      expect(result).not.toContainEqual(org1Field);
    });

    it("should include fields assigned to multiple orgs if selected publisher matches", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: userWithRolesManage,
        selectedPublisherId: "3",
      });

      expect(result).toHaveLength(3);
      expect(result).toContainEqual(globalField);
      expect(result).toContainEqual(nullOrgField);
      expect(result).toContainEqual(multiOrgField);
      expect(result).not.toContainEqual(org1Field);
    });
  });

  describe("Global access users (multi-tenants disabled)", () => {
    const userWithMultiTenantsDisabled = {
      id: 2,
      username: "single-tenant-admin",
      email: "admin@example.com",
      permissions: [],
      current_organisation: { id: 2, name: "Org 2" },
      feature_options: {
        enable_multi_tenants: false,
      },
    } as unknown as ResourceUserType;

    it("should show all fields when multi-tenants is disabled", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: userWithMultiTenantsDisabled,
        selectedPublisherId: null,
      });

      expect(result).toHaveLength(5);
      expect(result).toEqual(allFields);
    });

    it("should show all fields even when publisher is selected", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: userWithMultiTenantsDisabled,
        selectedPublisherId: "1",
      });

      expect(result).toHaveLength(5);
      expect(result).toEqual(allFields);
    });
  });

  describe("Regular users (multi-tenant enabled, no roles:manage)", () => {
    const regularUser = {
      id: 3,
      username: "regular-user",
      email: "user@example.com",
      permissions: [],
      current_organisation: { id: 1, name: "Org 1" },
      feature_options: {
        enable_multi_tenants: true,
      },
    } as unknown as ResourceUserType;

    it("should show global fields and fields from user's organisation", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: regularUser,
        selectedPublisherId: null,
      });

      expect(result).toHaveLength(4);
      expect(result).toContainEqual(globalField);
      expect(result).toContainEqual(nullOrgField);
      expect(result).toContainEqual(org1Field);
      expect(result).toContainEqual(multiOrgField);
    });

    it("should ignore selectedPublisherId for regular users", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: regularUser,
        selectedPublisherId: "2",
      });

      // Should still show user's org fields, not publisher's
      expect(result).toHaveLength(4);
      expect(result).toContainEqual(globalField);
      expect(result).toContainEqual(nullOrgField);
      expect(result).toContainEqual(org1Field);
      expect(result).toContainEqual(multiOrgField);
    });

    it("should include fields assigned to multiple orgs if user's org matches", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: regularUser,
        selectedPublisherId: null,
      });

      expect(result).toHaveLength(4);
      expect(result).toContainEqual(globalField);
      expect(result).toContainEqual(nullOrgField);
      expect(result).toContainEqual(org1Field);
      expect(result).toContainEqual(multiOrgField);
    });
  });

  describe("Edge cases", () => {
    it("should return all fields when user is null", () => {
      const result = filterFormFieldsByOrganisation(allFields, {
        user: null,
        selectedPublisherId: null,
      });

      // With null user, hasGlobalAccess is true (because enable_multi_tenants is falsy)
      expect(result.length).toBeGreaterThan(0);
    });

    it("should handle empty fields array", () => {
      const result = filterFormFieldsByOrganisation([], {
        user: null,
        selectedPublisherId: null,
      });

      expect(result).toEqual([]);
    });

    it("should treat fields with null organisation_ids as global", () => {
      const result = filterFormFieldsByOrganisation([nullOrgField], {
        user: {
          id: 1,
          username: "user",
          email: "user@example.com",
          permissions: [],
          current_organisation: { id: 99, name: "Org 99" },
          feature_options: { enable_multi_tenants: true },
        } as unknown as ResourceUserType,
        selectedPublisherId: null,
      });

      expect(result).toContainEqual(nullOrgField);
    });

    it("should treat fields with empty organisation_ids array as global", () => {
      const result = filterFormFieldsByOrganisation([globalField], {
        user: {
          id: 1,
          username: "user",
          email: "user@example.com",
          permissions: [],
          current_organisation: { id: 99, name: "Org 99" },
          feature_options: { enable_multi_tenants: true },
        } as unknown as ResourceUserType,
        selectedPublisherId: null,
      });

      expect(result).toContainEqual(globalField);
    });
  });
});

describe("sortFormFieldsByLabel", () => {
  it("should sort fields alphabetically by label (case-insensitive)", () => {
    const fields = [
      { label: "Zebra", value: "z" },
      { label: "apple", value: "a" },
      { label: "Banana", value: "b" },
    ];

    const result = sortFormFieldsByLabel(fields);

    expect(result[0].label).toBe("apple");
    expect(result[1].label).toBe("Banana");
    expect(result[2].label).toBe("Zebra");
  });

  it("should handle empty array", () => {
    const result = sortFormFieldsByLabel([]);
    expect(result).toEqual([]);
  });

  it("should handle single item", () => {
    const fields = [{ label: "Single", value: "s" }];
    const result = sortFormFieldsByLabel(fields);
    expect(result).toEqual(fields);
  });

  it("should sort special characters correctly", () => {
    const fields = [
      { label: "Éclair", value: "e" },
      { label: "Apple", value: "a" },
      { label: "Éléphant", value: "el" },
    ];

    const result = sortFormFieldsByLabel(fields);

    expect(result[0].label).toBe("Apple");
    expect(result[1].label).toBe("Éclair");
    expect(result[2].label).toBe("Éléphant");
  });
});
