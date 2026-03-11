import { z } from "zod";

export const AssignRoleFormSchema = z.object({
  email: z.string().email(),
  organisationId: z.number(),
  roleId: z.number(),
});
