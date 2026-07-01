import { Workflow } from "../types/workflow";

export const defaultWorkflow: Workflow = {
  id: "youtube-automation",
  name: "YouTube Automation Workflow",
  description: "Default CreatorOS workflow for fully automated video creation.",
  steps: [
    {
      id: "planner",
      name: "Planning",
      agentId: "planner",
      status: "pending",
    },
    {
      id: "research",
      name: "Research",
      agentId: "research",
      status: "pending",
    },
    {
      id: "script",
      name: "Script Generation",
      agentId: "script",
      status: "pending",
    },
    {
      id: "video",
      name: "Video Generation",
      agentId: "video",
      status: "pending",
    },
    {
      id: "publisher",
      name: "Publishing",
      agentId: "publisher",
      status: "pending",
    },
  ],
};