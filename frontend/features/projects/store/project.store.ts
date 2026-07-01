import { create } from "zustand";
import { getProjects } from "../services/project.service";

export interface Project {
  id: number;
  name: string;
  description: string;
}

interface ProjectStore {
  projects: Project[];
  loading: boolean;

  loadProjects: () => Promise<void>;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: [],
  loading: false,

  loadProjects: async () => {
    set({ loading: true });

    try {
      const data = await getProjects();

      set({
        projects: data,
        loading: false,
      });
    } catch (error) {
      console.error(error);

      set({
        loading: false,
      });
    }
  },
}));