import { listUsers } from "../../api/admin";
import { useQuery } from "@tanstack/react-query";
import type { User } from "../../types/auth";

export const useUsers = (
  role?: User["role"] | undefined,
  approvalState?: boolean | undefined,
) => {
  return useQuery({
    queryFn: () => listUsers(role, approvalState),
    queryKey: ["users", role, approvalState],
  });
};
