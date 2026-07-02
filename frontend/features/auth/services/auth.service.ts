import {
  login as loginApi,
  register as registerApi,
} from "../api/auth.api";

import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
} from "../types/auth.types";

export async function login(
  payload: LoginRequest
): Promise<LoginResponse> {
  return loginApi(payload);
}

export async function register(
  payload: RegisterRequest
): Promise<void> {
  await registerApi(payload);
}