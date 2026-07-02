"use client";

import { create } from "zustand";

import {
  getCurrentUser,
  login,
  logout,
  register,
  type LoginRequest,
  type RegisterRequest,
  type User,
} from "@/lib/api/auth";

interface AuthStore {
  user: User | null;
  loading: boolean;
  authenticated: boolean;

  login: (payload: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<void>;
  loadUser: () => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  loading: false,
  authenticated: false,

  async login(payload) {
    set({ loading: true });

    await login(payload);

    const user = await getCurrentUser();

    set({
      user,
      authenticated: true,
      loading: false,
    });
  },

  async register(payload) {
    await register(payload);
  },

  async loadUser() {
    try {
      const user = await getCurrentUser();

      set({
        user,
        authenticated: true,
      });
    } catch {
      set({
        user: null,
        authenticated: false,
      });
    }
  },

  logout() {
    logout();

    set({
      user: null,
      authenticated: false,
    });
  },
}));