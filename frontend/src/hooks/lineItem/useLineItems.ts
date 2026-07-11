import { useQuery } from "@tanstack/react-query";
import { listLineItems } from "../../api/serviceLineItem";

export const useLineItems = (serviceRequestId: string) => {
  return useQuery({
    queryKey: ["line-items", serviceRequestId],
    queryFn: () => listLineItems(serviceRequestId),
  });
};
