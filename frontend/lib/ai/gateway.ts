import apiClient from "@/lib/api/client";

export interface AICommandRequest {
  projectId: string;
  command: string;
}

export interface AICommandResponse {
  success: boolean;
  command: string;
  agent: string;
  status: string;
  result: string;
}

export async function executeAICommand(
  payload: AICommandRequest
): Promise<AICommandResponse> {
  const response = await apiClient.post(
    "/api/v1/commands/run",
    {
      command: payload.command,
    }
  );

  return response.data;
}