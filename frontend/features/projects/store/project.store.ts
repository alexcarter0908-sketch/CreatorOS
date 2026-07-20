"use client";

import { create } from "zustand";

import type { CreateProjectPayload, Project } from "../types/project";
import {
  createProject as createProjectService,
  getProject,
  listProjects,
} from "../services/project.service";

interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  isLoadingCurrent: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  fetchProjectById: (id: string) => Promise<void>;
  addProject: (payload: CreateProjectPayload) => Promise<void>;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  currentProject: null,
  isLoading: false,
  isLoadingCurrent: false,
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

  async fetchProjectById(id) {
    set({ isLoadingCurrent: true, error: null });

    try {
      const project = await getProject(id);
      set({ currentProject: project, isLoadingCurrent: false });
    } catch {
      set({ isLoadingCurrent: false, error: "Failed to load project." });
    }
  },

  async addProject(payload) {
    const project = await createProjectService(payload);
    set({ projects: [project, ...get().projects] });
  },
}));