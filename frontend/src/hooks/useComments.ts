import { useQuery } from "@tanstack/react-query";
import { list_comments } from "../api/comment";

export const useComments = (service_request_id: string) => {
  return useQuery({
    queryKey: ["comments", service_request_id],
    queryFn: () => list_comments(service_request_id),
  });
};
