export const COMMAND_STATUS = {
  PENDING: "Pending",
  RUNNING: "Running",
  COMPLETED: "Completed",
  FAILED: "Failed",
} as const;

export type CommandStatus =
  (typeof COMMAND_STATUS)[keyof typeof COMMAND_STATUS];

export interface Command {
  id: string;
  prompt: string;
  status: CommandStatus;
  createdAt: string;
}