import { useMutation, useQueryClient } from "@tanstack/react-query";
import { create_line_item } from "../../api/serviceLineItem";

export const useCreateLineItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: create_line_item,
    onSuccess: (data) =>
      queryClient.invalidateQueries({
        queryKey: ["line-items", data.service_request_id],
      }),
  });
};
