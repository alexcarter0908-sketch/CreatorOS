import { z } from "zod";

export const projectSchema = z.object({
  name: z
    .string()
    .min(3, "Project name must contain at least 3 characters")
    .max(80),

  description: z
    .string()
    .min(10, "Description must contain at least 10 characters")
    .max(500),
});

export type ProjectFormData = z.infer<typeof projectSchema>;