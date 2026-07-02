export type WorkflowStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

export interface WorkflowStep {
  id: string;
  name: string;
  agentId: string;
  status: WorkflowStatus;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
}