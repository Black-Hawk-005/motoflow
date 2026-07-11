import { useQuery } from "@tanstack/react-query";
import { list_line_items } from "../../api/serviceLineItem";

export const useLineItems = (service_request_id: string) => {
  return useQuery({
    queryKey: ["line-items", service_request_id],
    queryFn: () => list_line_items(service_request_id),
  });
};
