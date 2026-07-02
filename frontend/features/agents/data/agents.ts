import { Agent } from "../types/agent";

export const agents: Agent[] = [
  {
    id: "planner",
    name: "Planner Agent",
    description: "Breaks user goals into executable tasks.",
    status: "idle",
    version: "1.0.0",
  },
  {
    id: "research",
    name: "Research Agent",
    description: "Collects information and trending content.",
    status: "idle",
    version: "1.0.0",
  },
  {
    id: "script",
    name: "Script Agent",
    description: "Generates scripts and dialogue.",
    status: "idle",
    version: "1.0.0",
  },
  {
    id: "video",
    name: "Video Agent",
    description: "Creates videos from generated assets.",
    status: "idle",
    version: "1.0.0",
  },
  {
    id: "publisher",
    name: "Publisher Agent",
    description: "Publishes content to connected platforms.",
    status: "idle",
    version: "1.0.0",
  },
];