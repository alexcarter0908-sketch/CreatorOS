"use client";

import { create } from "zustand";

import {
  login as loginService,
  register as registerService,
} from "../services/auth.service";

import type {
  AuthState,
  LoginRequest,
  RegisterRequest,
  User,
} from "../types/auth.types";

interface AuthStore extends AuthState {
  login: (payload: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,

  async login(payload) {
    set({ isLoading: true });

    const tokens = await loginService(payload);

    localStorage.setItem(
      "creatoros_access_token",
      tokens.access_token
    );

    set({
      tokens,
      isAuthenticated: true,
      isLoading: false,
    });
  },

  async register(payload) {
    await registerService(payload);
  },

  logout() {
    localStorage.removeItem("creatoros_access_token");

    set({
      user: null,
      tokens: null,
      isAuthenticated: false,
    });
  },

  setUser(user) {
    set({ user });
  },
}));