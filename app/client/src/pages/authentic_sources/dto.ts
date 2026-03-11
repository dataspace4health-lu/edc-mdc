import { z } from "zod";

export const AuthenticSouceLabelFormSchema = z.object({
  name: z.string().nonempty(),
  description: z.string().nonempty(),
});
