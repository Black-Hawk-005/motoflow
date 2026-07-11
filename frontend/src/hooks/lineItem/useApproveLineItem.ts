import { useMutation, useQueryClient } from "@tanstack/react-query";
import { approveLineItem } from "../../api/serviceLineItem";

export const useApproveLineItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: approveLineItem,
    onSuccess: (data) =>
      queryClient.invalidateQueries({
        queryKey: ["line-items", data.service_request_id],
      }),
  });
};
