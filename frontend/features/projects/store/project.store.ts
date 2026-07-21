"use client";

import { create } from "zustand";

import type { Asset } from "@/features/assets/types/asset";
import type { CreateProjectPayload, Project, UpdateProjectPayload } from "../types/project";
import {
  createProject as createProjectService,
  deleteProject as deleteProjectService,
  getProject,
  listProjectAssets,
  listProjects,
  updateProject as updateProjectService,
} from "../services/project.service";

interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  currentProjectAssets: Asset[];
  isLoading: boolean;
  isLoadingCurrent: boolean;
  isLoadingAssets: boolean;
  isSaving: boolean;
  isDeleting: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  fetchProjectById: (id: string) => Promise<void>;
  fetchProjectAssets: (id: string) => Promise<void>;
  addProject: (payload: CreateProjectPayload) => Promise<void>;
  editProject: (id: string, payload: UpdateProjectPayload) => Promise<boolean>;
  removeProject: (id: string) => Promise<boolean>;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  currentProject: null,
  currentProjectAssets: [],
  isLoading: false,
  isLoadingCurrent: false,
  isLoadingAssets: false,
  isSaving: false,
  isDeleting: false,
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

  async fetchProjectAssets(id) {
    set({ isLoadingAssets: true });

    try {
      const assets = await listProjectAssets(id);
      set({ currentProjectAssets: assets, isLoadingAssets: false });
    } catch {
      set({ isLoadingAssets: false });
    }
  },

  async addProject(payload) {
    const project = await createProjectService(payload);
    set({ projects: [project, ...get().projects] });
  },

  async editProject(id, payload) {
    set({ isSaving: true, error: null });

    try {
      const updated = await updateProjectService(id, payload);
      set({
        currentProject: updated,
        projects: get().projects.map((p) => (p.id === id ? updated : p)),
        isSaving: false,
      });
      return true;
    } catch {
      set({ isSaving: false, error: "Failed to update project." });
      return false;
    }
  },

  async removeProject(id) {
    set({ isDeleting: true, error: null });

    try {
      await deleteProjectService(id);
      set({
        projects: get().projects.filter((p) => p.id !== id),
        currentProject: null,
        isDeleting: false,
      });
      return true;
    } catch {
      set({ isDeleting: false, error: "Failed to delete project." });
      return false;
    }
  },
}));
