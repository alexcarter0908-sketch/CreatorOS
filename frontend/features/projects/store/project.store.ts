import { create } from "zustand";
import { Project } from "../types/project";
import { getProjects } from "../services/project.service";

interface ProjectStore {
  projects: Project[];
  addProject: (project: Project) => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: getProjects(),

  addProject: (project) =>
    set((state) => ({
      projects: [...state.projects, project],
    })),
}));