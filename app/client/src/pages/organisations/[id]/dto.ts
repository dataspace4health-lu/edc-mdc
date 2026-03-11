import { z } from "zod";

export const ContactFormInputSchema = z.object({
  name: z.string().nonempty(),
  email: z.string().nonempty(),
  role: z.string().optional(),
});
