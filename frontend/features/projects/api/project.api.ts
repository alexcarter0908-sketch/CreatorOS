import { apiRequest } from "@/lib/api/client";

export interface Project {
  id: number;
  name: string;
  description: string;
}

export interface ProjectPayload {
  name: string;
  description: string;
}

export async function fetchProjects() {
  return apiRequest<Project[]>("/api/v1/projects/");
}

export async function createProject(data: ProjectPayload) {
  return apiRequest<Project>("/api/v1/projects/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateProject(
  id: number,
  data: ProjectPayload
) {
  return apiRequest<Project>(`/api/v1/projects/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteProject(id: number) {
  return apiRequest(`/api/v1/projects/${id}`, {
    method: "DELETE",
  });
}