import apiClient from "@/lib/api/client";
import type { CreateProjectPayload, Project } from "../types/project";

export async function listProjects(): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/api/v1/projects");
  return data;
}

export async function createProject(
  payload: CreateProjectPayload
): Promise<Project> {
  const { data } = await apiClient.post<Project>("/api/v1/projects", payload);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/projects/${id}`);
}