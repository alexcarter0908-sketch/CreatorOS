export const AUTH_ENDPOINTS = {
  REGISTER: "/api/v1/auth/register",
  LOGIN: "/api/v1/auth/login",
  ME: "/api/v1/auth/me",
  LOGOUT: "/api/v1/auth/logout",
} as const;

export const AUTH_STORAGE_KEYS = {
  ACCESS_TOKEN: "creatoros_access_token",
} as const;