import { z } from "zod";

export const OrganisationFormInputsSchema = z.object({
  name: z.string().nonempty(),
  type: z.string().optional(),
  email: z.string().email().optional(),
  category: z.string().optional(),
  accessible_within_ctie: z.string().optional(),
});
