export type AgentStatus =
  | "idle"
  | "running"
  | "paused"
  | "offline";

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  version: string;
}