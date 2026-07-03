import { useMutation, useQueryClient } from "@tanstack/react-query";
import { approveServiceRequest } from "../api/serviceRequest";

export const useApproveServiceRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: approveServiceRequest,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["service-requests"] }),
  });
};
