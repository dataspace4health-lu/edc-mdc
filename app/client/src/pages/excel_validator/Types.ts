export type ValidationResult = {
  valid: boolean;
  missingSheets: string[];
  missingHeaders: Record<string, string[]>;
  dataErrors: Record<string, string[]>;
};

export type RawContact = {
  value: string;
  eng_label: string;
  parent_value: string;
};

export type FormFields = {
  organisation?: {
    organisations: Array<{
      value: string;
      eng_label: string;
      is_deprecated: boolean | null;
      accessible_within_ctie?: boolean | null;
    }>;
  };
  contact?: {
    contacts: RawContact[];
  };
};
