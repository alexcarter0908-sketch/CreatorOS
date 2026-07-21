import apiClient from "@/lib/api/client";
import type { WorkflowApi } from "../types/workflow-api";

export async function listWorkflowsApi(): Promise<WorkflowApi[]> {
  const { data } = await apiClient.get<WorkflowApi[]>("/api/v1/workflows");
  return data;
}
