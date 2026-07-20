"use client";

import { create } from "zustand";

import {
  createTarget as createTargetService,
  deleteTarget as deleteTargetService,
  listTargets,
} from "../services/target.service";
import type { AutoTarget, CreateAutoTargetPayload } from "../types/target";

interface AutoTargetStore {
  targets: AutoTarget[];
  isLoading: boolean;
  error: string | null;
  fetchTargets: () => Promise<void>;
  addTarget: (payload: CreateAutoTargetPayload) => Promise<void>;
  removeTarget: (id: string) => Promise<void>;
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
}));