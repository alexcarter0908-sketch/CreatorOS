"use client";

import { create } from "zustand";

import { ACCESS_TOKEN_KEY } from "@/lib/api/client";
import {
  login as loginService,
  register as registerService,
  getCurrentUser,
} from "../services/auth.service";

import type {
  AuthState,
  LoginRequest,
  RegisterRequest,
  User,
} from "../types/auth.types";

interface AuthStore extends AuthState {
  login: (payload: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<string>;
  logout: () => void;
  setUser: (user: User | null) => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  isHydrated: false,

  async login(payload) {
    set({ isLoading: true });

    try {
      const tokens = await loginService(payload);
      const user = await getCurrentUser();

      set({
        user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  async register(payload) {
    set({ isLoading: true });

    try {
      const { email } = await registerService(payload);
      set({ isLoading: false });
      return email;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem("creatoros_active_conversation");

    set({
      user: null,
      tokens: null,
      isAuthenticated: false,
    });
  },

  setUser(user) {
    set({ user });
  },

  async hydrate() {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);

    if (!token) {
      set({ isHydrated: true });
      return;
    }

    try {
      const user = await getCurrentUser();

      set({
        user,
        tokens: { access_token: token, token_type: "bearer" },
        isAuthenticated: true,
        isHydrated: true,
      });
    } catch {
      localStorage.removeItem(ACCESS_TOKEN_KEY);

      set({
        user: null,
        tokens: null,
        isAuthenticated: false,
        isHydrated: true,
      });
    }
  },
}));
