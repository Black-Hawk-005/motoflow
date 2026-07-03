import axiosClient from "./client";

import type {
  ServiceRequestResponse,
  ServiceRequestCreatePayload,
} from "../types/ServiceRequest";

export const listServiceRequests = async (): Promise<
  ServiceRequestResponse[]
> => {
  const response =
    await axiosClient.get<ServiceRequestResponse[]>("/service-requests/");
  return response.data;
};

export const getServiceRequest = async (
  service_request_id: string,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.get<ServiceRequestResponse>(
    `/service-requests/${service_request_id}`,
  );
  return response.data;
};

export const createServiceRequest = async (
  service_request_details: ServiceRequestCreatePayload,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.post<ServiceRequestResponse>(
    "/service-requests/",
    service_request_details,
  );
  return response.data;
};

export const approveServiceRequest = async (
  service_request_id: string,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.patch<ServiceRequestResponse>(
    `/service-requests/${service_request_id}/approve`,
  );
  return response.data;
};
