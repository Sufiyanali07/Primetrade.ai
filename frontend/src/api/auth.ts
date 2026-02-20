import { api } from "./client";
import type { LoginRequest, RegisterRequest, TokenResponse, User } from "@/types";

export async function register(data: RegisterRequest): Promise<User> {
  const res = await api.post<User>("/api/v1/auth/register", data);
  return res.data;
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>("/api/v1/auth/login", data);
  return res.data;
}
