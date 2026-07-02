import apiClient from "@/lib/api/client";

export interface AICommandRequest {
  projectId: string;
  command: string;
}

export interface AICommandResponse {
  executionId: string;
  status: "accepted" | "running" | "completed" | "failed";
}

export async function executeAICommand(
  payload: AICommandRequest
): Promise<AICommandResponse> {
  const response = await apiClient.post(
    "/api/v1/commands/execute",
    payload
  );

  return response.data;
}