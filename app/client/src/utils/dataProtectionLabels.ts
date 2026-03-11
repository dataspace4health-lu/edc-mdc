const dataProtectionTypes = [
  "CommerciallyConfidentialData",
  "StatisticallyConfidentialData",
  "IntellectualPropertyData",
  "PersonalData",
  "SpecialCategoryPersonalData",
  "ProfessionalConfidentialData",
];

export const toReadableFormat = (label: string) => {
  return label.replace(/([a-z])([A-Z])/g, "$1 $2");
};

export const dataProtectionTypeLabels = dataProtectionTypes.map(toReadableFormat);

export const dataProtectionTypeOptions = dataProtectionTypes.map((type) => ({
  label: toReadableFormat(type),
  value: type,
}));
