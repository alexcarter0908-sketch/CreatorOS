// Types for the REAL backend workflow API (GET /api/v1/workflows),
// separate from the mock `Workflow` type in ./workflow.ts which is
// unused scaffolding not wired to any API.

export type WorkflowStepStatus = "pending" | "running" | "completed" | "failed";
export type WorkflowRunStatus =
  | "draft"
  | "running"
  | "completed"
  | "completed_with_errors"
  | "failed";

export interface WorkflowStepApi {
  id: string;
  order_index: number;
  asset_type: string;
  prompt: string;
  status: WorkflowStepStatus;
  asset_id: string | null;
  error_message: string | null;
}

export interface WorkflowApi {
  id: string;
  name: string;
  status: WorkflowRunStatus;
  project_id: string | null;
  created_at: string | null;
  steps: WorkflowStepApi[];
}
