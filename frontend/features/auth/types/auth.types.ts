export interface User {
  id: string;
  full_name: string;
  email: string;
  avatar_url: string | null;
  is_active: boolean;
  is_superuser: boolean;
  is_email_verified: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  detail: string;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface VerifyEmailRequest {
  email: string;
  otp_code: string;
}

export interface UpdateProfileRequest {
  full_name?: string;
  avatar_url?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface AuthState {
  user: User | null;
  tokens: TokenResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isHydrated: boolean;
}