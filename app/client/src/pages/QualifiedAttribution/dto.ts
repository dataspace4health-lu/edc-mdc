import { z } from "zod";

export type QualifiedAttributionRoleOption = {
  value: string;
  label: string;
};

export const QualifiedAttributionRoleOptions: QualifiedAttributionRoleOption[] = [
  { value: "author", label: "Author" },
  { value: "custodian", label: "Custodian" },
  { value: "distributor", label: "Distributor" },
  { value: "originator", label: "Originator" },
  { value: "owner", label: "Owner" },
  { value: "pointOfContact", label: "Point Of Contact" },
  { value: "principalInvestigator", label: "Principal Investigator" },
  { value: "processor", label: "Processor" },
  { value: "resourceProvider", label: "Resource Provider" },
  { value: "user", label: "User" },
];

export const QualifiedAttributionSchema = z.object({
  datasetId: z.string().nonempty(),
  organisationId: z.string().nonempty("Organisation is required"),
  role: z.string().nonempty("Role is required"),
});

export type QualifiedAttributionFormData = z.infer<typeof QualifiedAttributionSchema>;
