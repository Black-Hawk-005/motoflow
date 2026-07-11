import { useMutation, useQueryClient } from "@tanstack/react-query";
import { create_comment } from "../../api/comment";

export const useCreateComment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: create_comment,
    onSuccess: (data) =>
      queryClient.invalidateQueries({
        queryKey: ["comments", data.service_request_id],
      }),
  });
};
