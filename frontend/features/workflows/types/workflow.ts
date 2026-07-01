export type WorkflowStatus =
  | "Draft"
  | "Ready"
  | "Running"
  | "Completed"
  | "Failed";

export interface WorkflowStep {
  id: string;
  name: string;
  completed: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  status: WorkflowStatus;
  steps: WorkflowStep[];
  createdAt: string;
  updatedAt: string;
}