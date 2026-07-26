import type { AdminUserCreatePayload, User } from "../types/auth";
import axiosClient from "./client";

export const listUsers = async (
  role?: User["role"],
  approval_state?: boolean,
): Promise<User[]> => {
  if (role !== undefined && approval_state !== undefined) {
    const response = await axiosClient.get<Promise<User[]>>(
      `/admin/users?role=${role}&approval_state=${approval_state}`,
    );
    return response.data;
  } else if (role !== undefined) {
    const response = await axiosClient.get<Promise<User[]>>(
      `/admin/users?role=${role}`,
    );
    return response.data;
  } else if (approval_state !== undefined) {
    const response = await axiosClient.get<Promise<User[]>>(
      `/admin/users?approval_state=${approval_state}`,
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

export const approveUser = async (user_id: string): Promise<User> => {
  const response = await axiosClient.patch<User>(
    `/admin/users/${user_id}/approve`,
  );
  return response.data;
};
