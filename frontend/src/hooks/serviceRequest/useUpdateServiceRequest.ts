import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateServiceRequest } from "../../api/serviceRequest";
import type { ServiceRequestUpdatePayload } from "../../types/serviceRequest";

export const useUpdateServiceRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: {
      id: string;
      payload: ServiceRequestUpdatePayload;
    }) => updateServiceRequest(variables.id, variables.payload),
    onSuccess: () => {
      queryClient
        .invalidateQueries({ queryKey: ["service-requests"] })
        .catch(() => {});
    },
  });
};
