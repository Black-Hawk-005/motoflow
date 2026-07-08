import { useMutation, useQueryClient } from "@tanstack/react-query";
import { approve_line_item } from "../api/serviceLineItem";

export const useApproveLineItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: approve_line_item,
    onSuccess: (data) =>
      queryClient.invalidateQueries({
        queryKey: ["line-items", data.service_request_id],
      }),
  });
};
