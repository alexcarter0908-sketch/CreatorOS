import { Project } from "../types/project";

export const projects: Project[] = [
  {
    id: crypto.randomUUID(),
    name: "Tech News Daily",
    description: "Daily AI news videos",
    status: "Active",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: crypto.randomUUID(),
    name: "Finance Explained",
    description: "Educational finance content",
    status: "Draft",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: crypto.randomUUID(),
    name: "History Documentary",
    description: "Historical documentary channel",
    status: "Completed",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export function getProjects() {
  return projects;
}