import { z } from "zod";

const EndpointSchema = z.object({
  endpoint_url: z.string().url(),
  endpoint_description: z.string().optional(),
});

export const DataServiceFormSchema = z.object({
  title: z.string().nonempty(),
  endpoints: z.array(EndpointSchema).min(1, "At least one endpoint is required"),
});

export type EndpointFormType = z.infer<typeof EndpointSchema>;
