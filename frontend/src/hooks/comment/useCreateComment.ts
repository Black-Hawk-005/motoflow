import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createComment } from "../../api/comment";

export const useCreateComment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createComment,
    onSuccess: (data) =>
      queryClient.invalidateQueries({
        queryKey: ["comments", data.service_request_id],
      }),
  });
};
