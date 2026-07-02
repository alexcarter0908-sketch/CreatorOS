import { create } from "zustand";
import { Workflow } from "../types/workflow";
import { getWorkflows } from "../services/workflow.service";

interface WorkflowStore {
  workflows: Workflow[];
  addWorkflow: (workflow: Workflow) => void;
}

export const useWorkflowStore = create<WorkflowStore>((set) => ({
  workflows: getWorkflows(),

  addWorkflow: (workflow) =>
    set((state) => ({
      workflows: [...state.workflows, workflow],
    })),
}));