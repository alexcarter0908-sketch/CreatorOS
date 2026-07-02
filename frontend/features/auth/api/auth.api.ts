import apiClient from "@/lib/api/client";

import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
} from "../types/auth.types";

export async function login(
  data: LoginRequest
): Promise<LoginResponse> {

  const form = new URLSearchParams();

  form.append("username", data.email);
  form.append("password", data.password);

  const response = await apiClient.post(
    "/api/v1/auth/login",
    form,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
}

export async function register(
  data: RegisterRequest
): Promise<void> {

  await apiClient.post(
    "/api/v1/auth/register",
    data
  );

}