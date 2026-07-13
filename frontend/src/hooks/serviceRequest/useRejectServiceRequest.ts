import { useMutation, useQueryClient } from "@tanstack/react-query";
import { rejectServiceRequest } from "../../api/serviceRequest";
import type { ServiceRequestRejectPayload } from "../../types/serviceRequest";

export const useRejectServiceRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: {
      id: string;
      payload: ServiceRequestRejectPayload;
    }) => rejectServiceRequest(variables.id, variables.payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["service-requests"],
      });
      queryClient.invalidateQueries({
        queryKey: ["comments", data.id],
      });
    },
  });
};
