import api from "./client";

export type UserRole =
  | "citizen"
  | "responder"
  | "admin";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  full_name: string;
  email: string;
  password: string;
}

export async function login(
  credentials: LoginCredentials
): Promise<TokenResponse> {
  const formData = new URLSearchParams();

  formData.append("username", credentials.email);
  formData.append("password", credentials.password);

  const response = await api.post<TokenResponse>(
    "/auth/login",
    formData,
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
  data: RegisterData
): Promise<User> {
  const response = await api.post<User>(
    "/auth/register",
    data
  );

  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>(
    "/users/me"
  );

  return response.data;
}