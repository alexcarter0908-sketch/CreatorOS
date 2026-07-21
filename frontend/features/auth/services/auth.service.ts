import apiClient, { ACCESS_TOKEN_KEY } from "@/lib/api/client";
import type {
  ChangePasswordRequest,
  DeleteAccountRequest,
  LoginRequest,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
  UpdateProfileRequest,
  User,
  VerifyEmailRequest,
} from "../types/auth.types";

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.set("username", payload.email);
  form.set("password", payload.password);

  const { data } = await apiClient.post<TokenResponse>(
    "/api/v1/auth/login",
    form,
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    }
  );
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  return data;
}

export async function register(payload: RegisterRequest): Promise<RegisterResponse> {
  const { data } = await apiClient.post<RegisterResponse>(
    "/api/v1/auth/register",
    payload
  );
  return data;
}

export async function verifyEmail(payload: VerifyEmailRequest): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>(
    "/api/v1/auth/verify-email",
    payload
  );
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  return data;
}

export async function resendVerification(email: string): Promise<void> {
  await apiClient.post("/api/v1/auth/resend-verification", { email });
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>("/api/v1/users/me");
  return data;
}

export async function updateProfile(payload: UpdateProfileRequest): Promise<User> {
  const { data } = await apiClient.patch<User>("/api/v1/users/me", payload);
  return data;
}

export async function changePassword(payload: ChangePasswordRequest): Promise<void> {
  await apiClient.post("/api/v1/users/me/change-password", payload);
}

export async function deleteAccount(payload: DeleteAccountRequest): Promise<void> {
  await apiClient.delete("/api/v1/users/me", { data: payload });
  localStorage.removeItem(ACCESS_TOKEN_KEY);
}
