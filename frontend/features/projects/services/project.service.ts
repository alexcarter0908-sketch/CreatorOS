import apiClient from "@/lib/api/client";
import type { Asset } from "@/features/assets/types/asset";
import type { CreateProjectPayload, Project, UpdateProjectPayload } from "../types/project";

export async function listProjects(): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/api/v1/projects");
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await apiClient.get<Project>(`/api/v1/projects/${id}`);
  return data;
}

export async function updateProject(id: string, payload: UpdateProjectPayload): Promise<Project> {
  const { data } = await apiClient.patch<Project>(`/api/v1/projects/${id}`, payload);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/projects/${id}`);
}

export async function listProjectAssets(id: string): Promise<Asset[]> {
  const { data } = await apiClient.get<Asset[]>(`/api/v1/projects/${id}/assets`);
  return data;
}

export async function createProject(
  payload: CreateProjectPayload
): Promise<Project> {
  const { data } = await apiClient.post<Project>("/api/v1/projects", payload);
  return data;
}
