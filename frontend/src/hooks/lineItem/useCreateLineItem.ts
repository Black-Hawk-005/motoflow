import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createLineItem } from "../../api/serviceLineItem";

export const useCreateLineItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createLineItem,
    onSuccess: (data) =>
      queryClient.invalidateQueries({
        queryKey: ["line-items", data.service_request_id],
      }),
  });
};
