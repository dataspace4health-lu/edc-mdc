interface DatasetFieldDisplayNames {
  [key: string]: { label: string; longLabel: string };
}

export const relationsDisplayFields: DatasetFieldDisplayNames = {
  targetId: {
    label: "Dataset",
    longLabel: "Dataset",
  },
  relationType: {
    label: "Relation Type",
    longLabel: "Relation Type",
  },
  externalRole: {
    label: "Role",
    longLabel: "External Resource Role",
  },
};

export const statusDisplayNames: Record<string, string> = {
  DRAFT: "Draft",
  COMPLETED: "Completed",
  VALIDATED: "Validated",
  APPROVED: "Approved",
  INTERNAL_ONLY: "Internal Only",
  PUBLISHED: "Published",
  DEPRECATED: "DEPRECATED",
};
