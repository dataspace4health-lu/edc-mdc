export const rightStatementsLabels = {
  "http://publications.europa.eu/resource/authority/access-right/PUBLIC": "Public",
  "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC": "Non-Public",
};

export const rightStatementsOptions = Object.entries(rightStatementsLabels).map(
  ([value, eng_label]) => ({ eng_label, value }),
);
