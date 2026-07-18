import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createUser } from "../../api/admin";

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createUser,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
};
