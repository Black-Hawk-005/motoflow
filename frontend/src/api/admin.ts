import type { AdminUserCreatePayload, User } from "../types/auth";
import axiosClient from "./client";

export const listUsers = async (role?: User["role"]): Promise<User[]> => {
  if (role) {
    const response = await axiosClient.get<Promise<User[]>>(
      `/admin/users?role=${role}`,
    );
    return response.data;
  } else {
    const response = await axiosClient.get<Promise<User[]>>(`/admin/users`);
    return response.data;
  }
};

export const createUser = async (
  userData: AdminUserCreatePayload,
): Promise<User> => {
  const response = await axiosClient.post<User>(`/admin/users`, userData);
  return response.data;
};
