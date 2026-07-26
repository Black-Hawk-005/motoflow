import { useMutation, useQueryClient } from "@tanstack/react-query";
import { approveUser } from "../../api/admin";

export const useApproveUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: approveUser,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
};
