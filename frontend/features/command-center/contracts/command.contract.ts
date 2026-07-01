export type CommandPriority =
  | "low"
  | "normal"
  | "high";

export interface ExecuteCommandRequest {
  projectId: string;

  command: string;

  priority: CommandPriority;
}

export interface ExecuteCommandResponse {
  executionId: string;

  accepted: boolean;

  message: string;
}