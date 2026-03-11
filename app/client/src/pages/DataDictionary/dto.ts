import { z } from "zod";

type DictionaryTypeOption = {
  value: string;
  label: string;
};

export const options: DictionaryTypeOption[] = [
  { value: "String", label: "String" },
  { value: "Integer", label: "Integer" },
  { value: "Boolean", label: "Boolean" },
  { value: "Float", label: "Float" },
  { value: "Character", label: "Character" },
  { value: "Byte", label: "Byte" },
  { value: "Short", label: "Short" },
  { value: "Long", label: "Long" },
  { value: "Double", label: "Double" },
  { value: "Date", label: "Date" },
];

export const allowedDataTypes = [
  "String",
  "Integer",
  "Boolean",
  "Float",
  "Character",
  "Byte",
  "Short",
  "Long",
  "Double",
  "Date",
] as const;

export const privacyRiskOptions: DictionaryTypeOption[] = [
  { value: "Identifiant direct", label: "Identifiant direct" },
  { value: "Quasi-identifiant", label: "Quasi-identifiant" },
  { value: "Variable d'agrégation ", label: "Variable d'agrégation" },
  { value: "Valeur rare", label: "Valeur rare" },
  { value: "Autre risqué", label: "Autre risqué" },
];

export const DataDictionaryEntrySchema = z
  .object({
    name: z.string().nonempty(),
    type: z
      .string()
      .nonempty()
      .refine(
        (val) => {
          const lowerVal = val.toLowerCase();
          return allowedDataTypes.some((type) => type.toLowerCase() === lowerVal);
        },
        {
          message: `Type must be one of: ${allowedDataTypes.join(", ")}`,
        },
      ),
    description: z.string().nonempty(),
    personallyIdentifiableVariable: z.boolean().nullable().optional(),
    required: z.boolean().nullable().optional(),
    maxAllowedValue: z.number().optional(),
    minAllowedValue: z.number().optional(),
    variableUnit: z.string().optional(),
    allowedValues: z.string().optional(),
    allowedValuesDescription: z.string().optional(),
    privacyRisk: z.string().optional(),
  })
  .refine(
    () => {
      // will be added later
      // if (data.personallyIdentifiableVariable && !data.privacyRisk) {
      //   return false;
      // }
      return true;
    },
    {
      message: "Privacy risk must be provided if personally identifiable variable is true.",
      path: ["privacyRisk"],
    },
  );

export type DataDictionaryEntry = z.infer<typeof DataDictionaryEntrySchema>;
