import axiosClient from "./client";
import type { LoginResponse, User, RegisterPayload } from "../types/auth";

export const login = async (
  email: string,
  password: string,
): Promise<LoginResponse> => {
  const params = new URLSearchParams();
  params.append("username", email);
  params.append("password", password);

  const response = await axiosClient.post<LoginResponse>(
    "/auth/login",
    params,
    { headers: { "Content-Type": "application/x-www-form-urlencoded" } },
  );
  return response.data;
};

export const register = async (data: RegisterPayload): Promise<User> => {
  const response = await axiosClient.post<User>("/auth/register", data);
  return response.data;
};

export const getMe = async (): Promise<User> => {
  const response = await axiosClient.get<User>("/auth/me");
  return response.data;
};
