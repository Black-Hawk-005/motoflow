import { useQuery } from "@tanstack/react-query";
import { listComments } from "../../api/comment";

export const useComments = (serviceRequestId: string) => {
  return useQuery({
    queryKey: ["comments", serviceRequestId],
    queryFn: () => listComments(serviceRequestId),
  });
};
