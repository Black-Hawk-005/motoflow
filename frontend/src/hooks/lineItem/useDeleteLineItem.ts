import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteLineItem } from "../../api/serviceLineItem";

export const useDeleteLineItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: { lineItemId: string; serviceRequestId: string }) =>
      deleteLineItem(variables.lineItemId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["line-items", variables.serviceRequestId],
      });
    },
  });
};
