import { listUsers } from "../../api/admin";
import { useQuery } from "@tanstack/react-query";
import type { User } from "../../types/auth";

export const useUsers = (role?: User["role"] | undefined) => {
  return useQuery({
    queryKey: ["users", role],
    queryFn: () => listUsers(role),
  });
};
