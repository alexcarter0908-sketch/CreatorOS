export const COMMAND_STATUS = {
  PENDING: "pending",
  COMPLETED: "completed",
  FAILED: "failed",
} as const;
export type CommandStatus = (typeof COMMAND_STATUS)[keyof typeof COMMAND_STATUS];
export type ChatRole = "user" | "assistant";
export type AttachmentKind = "image" | "video" | "audio" | "document";
export interface ChatAttachment {
  id: string;
  url: string;
  kind: AttachmentKind;
  name: string;
}
export interface ChatSource {
  title: string;
  url: string;
}
export interface WorkflowStepInfo {
  asset_type: string;
  status: string;
  error_message?: string | null;
}
export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  status: CommandStatus;
  assetType?: string;
  fileUrl?: string | null;
  errorMessage?: string | null;
  attachments?: ChatAttachment[];
  replyToText?: string;
  steps?: WorkflowStepInfo[];
  workflowId?: string;
  assetId?: string;
  hasFailedSteps?: boolean;
  sources?: ChatSource[];
}


