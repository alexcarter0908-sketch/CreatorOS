import { apiRequest } from "@/lib/api/client";

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
  return apiRequest<AICommandResponse>("/api/v1/commands/execute", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}