import { useQuery } from "@tanstack/react-query";
import { listServiceRequests } from "../../api/serviceRequest";

export const useServiceRequests = () => {
  return useQuery({
    queryKey: ["service-requests"],
    queryFn: listServiceRequests,
  });
};
