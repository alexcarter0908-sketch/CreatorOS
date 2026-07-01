export const PROJECT_STATUS = {
  ACTIVE: "Active",
  DRAFT: "Draft",
  COMPLETED: "Completed",
} as const;

export type ProjectStatus =
  (typeof PROJECT_STATUS)[keyof typeof PROJECT_STATUS];

export interface Project {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
}