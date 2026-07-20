import apiClient from "@/lib/api/client";

export interface AICommandHistoryTurn {
  role: "user" | "assistant";
  content: string;
}

export interface AICommandRequest {
  projectId: string;
  command: string;
  conversationId?: string | null;
  history?: AICommandHistoryTurn[];
  latitude?: number | null;
  longitude?: number | null;
}

export interface AICommandResponse {
  success: boolean;
  command: string;
  agent: string;
  status: string;
  result: string;
  asset_id?: string | null;
  conversation_id?: string;
  workflow_id?: string;
  text?: string;
}

export async function executeAICommand(
  payload: AICommandRequest
): Promise<AICommandResponse> {
  const response = await apiClient.post("/api/v1/commands/run", {
    command: payload.command,
    project_id: payload.projectId || null,
    conversation_id: payload.conversationId || null,
    history: payload.history ?? [],
    latitude: payload.latitude ?? null,
    longitude: payload.longitude ?? null,
  });
  return response.data;
}