import { DummyOrganisation } from "./organisation-fixture";

export const BulkUploadedDataset1 = {
  contact: "Saif",
  title: "Dataset title 1",
  publisherName: DummyOrganisation.name,
  description: "A useful dataset collected in situation x about interesting stuff y.",
  keywords: ["people"],
  themes: ["Health"],
  spatial_coverages: ["Luxembourg"],
  rights: "Public",
  types: ["Structured data"],
  periodicity: "annual",
  creatorNames: [DummyOrganisation.name],
  data_protection_types: ["Personal Data"],
  languages: ["Luxembourgish", "French"],
  applicableLegislations: ["Law #123, art 5"],
};

export const BulkUploadedDataset2 = {
  contact: "Saif",
  title: "Dataset title 2",
  publisherName: DummyOrganisation.name,
  description: "A useful dataset collected in situation x about interesting stuff y.",
  keywords: ["policy"],
  themes: ["Health"],
  spatial_coverages: ["Algeria"],
  rights: "Non-Public",
  types: ["Audiovisual"],
  periodicity: "biennial",
  creatorNames: [DummyOrganisation.name],
  data_protection_types: ["Intellectual Property Data"],
  languages: ["German"],
  applicableLegislations: ["Applicable Legislation"],
};

export const RightsLabelValueMapping: Record<string, string> = {
  "non-public": "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC",
  public: "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
};

export const ApplicableLegislationLabelValueMapping: Record<string, string> = {
  "General Data Protection Regulation": "GDPR",
};

export const LanguagesLabelValueMapping: Record<string, string> = {
  English: "http://publications.europa.eu/resource/authority/language/ENG",
  French: "http://publications.europa.eu/resource/authority/language/FRA",
};

export const Distribution = {
  title: "Stuff raw data",
  description: "Raw data collected as part of the stuff study",
  access_urls: ["https://www.stuff.lu/data_access_request"],
  format: "CSV",
  license: "Creative Commons Zero v1.0 Universal",
  rights: "Public",
  languages: ["French"],
  media_type: "application/yang-data+xml",
  compression_format: "application/yang-data+xml",
  packaging_format: "application/yang-data+xml",
  applicableLegislations: ["Applicable Legislation"],
  availability: "Available",
};

export const NonExistentContact = {
  name: "Saif",
  email: "saif@lnds.lu",
  role: "Manager",
};
