export type ProjectStatus = "draft" | "active" | "completed";

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  status_auto: boolean;
  brand_voice: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  brand_voice?: string;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string | null;
  status?: ProjectStatus;
  status_auto?: boolean;
  brand_voice?: string | null;
}
