"use client";

import { create } from "zustand";

import {
  createTarget as createTargetService,
  deleteTarget as deleteTargetService,
  listTargets,
  pauseTarget as pauseTargetService,
  resumeTarget as resumeTargetService,
} from "../services/target.service";
import type { AutoTarget, CreateAutoTargetPayload } from "../types/target";

interface AutoTargetStore {
  targets: AutoTarget[];
  isLoading: boolean;
  error: string | null;
  fetchTargets: () => Promise<void>;
  addTarget: (payload: CreateAutoTargetPayload) => Promise<void>;
  removeTarget: (id: string) => Promise<void>;
  toggleTarget: (id: string, isActive: boolean) => Promise<void>;
}

export const useAutoTargetStore = create<AutoTargetStore>((set, get) => ({
  targets: [],
  isLoading: false,
  error: null,

  async fetchTargets() {
    set({ isLoading: true, error: null });
    try {
      const targets = await listTargets();
      set({ targets, isLoading: false });
    } catch {
      set({ isLoading: false, error: "Failed to load automation targets." });
    }
  },

  async addTarget(payload) {
    const target = await createTargetService(payload);
    set({ targets: [target, ...get().targets] });
  },

  async removeTarget(id) {
    await deleteTargetService(id);
    set({ targets: get().targets.filter((t) => t.id !== id) });
  },

  async toggleTarget(id, isActive) {
    // isActive is the target's *current* state - true means it's running
    // now, so this call should pause it, and vice versa.
    const updated = isActive ? await pauseTargetService(id) : await resumeTargetService(id);
    set({
      targets: get().targets.map((t) => (t.id === id ? updated : t)),
    });
  },
}));
