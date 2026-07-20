"use client";

import { create } from "zustand";

import type { CreateProjectPayload, Project } from "../types/project";
import {
  createProject as createProjectService,
  listProjects,
} from "../services/project.service";

interface ProjectStore {
  projects: Project[];
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  addProject: (payload: CreateProjectPayload) => Promise<void>;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  isLoading: false,
  error: null,

  async fetchProjects() {
    set({ isLoading: true, error: null });

    try {
      const projects = await listProjects();
      set({ projects, isLoading: false });
    } catch {
      set({ isLoading: false, error: "Failed to load projects." });
    }
  },

  async addProject(payload) {
    const project = await createProjectService(payload);
    set({ projects: [project, ...get().projects] });
  },
}));