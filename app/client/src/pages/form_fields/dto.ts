import { z } from "zod";
import { ResourceFormField, ApplicableLegislationFormField } from "../../types";

export const FormInputsSchema = z.object({
  engLabel: z.string().nonempty(),
  description: z.string().optional(),
  link: z
    .string()
    .optional()
    .refine(
      (val) => {
        if (!val || val.trim() === "") return true; // Allow empty
        try {
          new URL(val);
          return true;
        } catch {
          return false;
        }
      },
      { message: "Link must be a valid URL (e.g., https://example.com)" },
    ),
  organisationIds: z.array(z.string()).optional(),
});

export type FormInputs = z.infer<typeof FormInputsSchema>;

export function toFormInputs(
  formField: ResourceFormField | ApplicableLegislationFormField,
): FormInputs {
  return {
    engLabel: formField.eng_label,
    description: (formField as ApplicableLegislationFormField).description || "",
    link: (formField as ApplicableLegislationFormField).link || "",
    organisationIds: Array.isArray(formField.organisation_ids)
      ? formField.organisation_ids.map((id) => id.toString())
      : formField.organisation_id
        ? [formField.organisation_id.toString()]
        : [],
  };
}
