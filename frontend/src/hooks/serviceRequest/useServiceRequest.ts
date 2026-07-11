import { useQuery } from "@tanstack/react-query";
import { getServiceRequest } from "../../api/serviceRequest";

export const useServiceRequest = (service_request_id: string) => {
  return useQuery({
    queryKey: ["service-requests", service_request_id],
    queryFn: () => getServiceRequest(service_request_id),
  });
};
