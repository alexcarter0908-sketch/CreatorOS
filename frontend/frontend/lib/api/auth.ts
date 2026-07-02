import apiClient, { ACCESS_TOKEN_KEY } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
  avatar_url: string | null;
  is_active: boolean;
  is_superuser: boolean;
}

export async function login(
  payload: LoginRequest
): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>(
    "/api/v1/auth/login",
    payload
  );

  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    data.access_token
  );

  return data;
}

export async function register(
  payload: RegisterRequest
): Promise<User> {
  const { data } = await apiClient.post<User>(
    "/api/v1/auth/register",
    payload
  );

  return data;
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>(
    "/api/v1/users/me"
  );

  return data;
}

export function logout() {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY
  );
}