import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateLineItem } from "../../api/serviceLineItem";
import type { ServiceLineItemUpdatePayload } from "../../types/serviceLineItem";

export const useUpdateLineItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variables: {
      id: string;
      updateDetails: ServiceLineItemUpdatePayload;
    }) => updateLineItem(variables.id, variables.updateDetails),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["line-items"],
      });
    },
  });
};
