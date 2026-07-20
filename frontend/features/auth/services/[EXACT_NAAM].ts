import apiClient, { ACCESS_TOKEN_KEY } from "@/lib/api/client";
import type {
  ChangePasswordRequest,
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

  // BUG FIX: apiClient has a default "Content-Type: application/json"
  // header. Passing an *empty* headers object here did NOT clear that
  // default, so this request was going out as JSON even though the body
  // was URL-encoded form data. The backend's OAuth2 form parser couldn't
  // read username/password from a JSON-labeled body, so login failed
  // every time - even with the correct password. Explicitly setting the
  // correct Content-Type below fixes that.
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
