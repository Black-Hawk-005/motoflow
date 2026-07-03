import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createServiceRequest } from "../api/serviceRequest";

export const useCreateServiceRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createServiceRequest,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["service-requests"] }),
  });
};
