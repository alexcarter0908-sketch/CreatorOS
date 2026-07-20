import apiClient from "@/lib/api/client";
import type { ChatMessage, ChatSource, CommandStatus } from "../types/command";

interface MessageResponse {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: string;
  asset_id: string | null;
  error_message: string | null;
  extra_metadata: Record<string, unknown> | null;
  created_at: string;
}

interface ConversationDetailResponse {
  id: string;
  title: string | null;
  messages: MessageResponse[];
}

function toCommandStatus(status: string): CommandStatus {
  if (status === "failed") return "failed";
  if (status === "pending") return "pending";
  return "completed";
}

export async function fetchConversation(conversationId: string): Promise<ChatMessage[]> {
  const { data } = await apiClient.get<ConversationDetailResponse>(
    `/api/v1/conversations/${conversationId}`
  );

  return data.messages.map((m) => {
    const meta = m.extra_metadata as { sources?: ChatSource[] } | null;

    return {
      id: m.id,
      role: m.role,
      content: m.content,
      createdAt: m.created_at,
      status: toCommandStatus(m.status),
      errorMessage: m.error_message,
      sources: meta?.sources,
    };
  });
}