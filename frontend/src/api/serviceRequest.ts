import axiosClient from "./client";

import type {
  ServiceRequestResponse,
  ServiceRequestCreatePayload,
  ServiceRequestUpdatePayload,
  ServiceRequestRejectPayload,
} from "../types/serviceRequest";

export const listServiceRequests = async (): Promise<
  ServiceRequestResponse[]
> => {
  const response =
    await axiosClient.get<ServiceRequestResponse[]>("/service-requests/");
  return response.data;
};

export const getServiceRequest = async (
  serviceRequestId: string,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.get<ServiceRequestResponse>(
    `/service-requests/${serviceRequestId}`,
  );
  return response.data;
};

export const createServiceRequest = async (
  serviceRequestDetails: ServiceRequestCreatePayload,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.post<ServiceRequestResponse>(
    "/service-requests/",
    serviceRequestDetails,
  );
  return response.data;
};

export const approveServiceRequest = async (
  serviceRequestId: string,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.patch<ServiceRequestResponse>(
    `/service-requests/${serviceRequestId}/approve`,
  );
  return response.data;
};

export const rejectServiceRequest = async (
  serviceRequestId: string,
  rejectRequestPayload: ServiceRequestRejectPayload,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.patch<ServiceRequestResponse>(
    `/service-requests/${serviceRequestId}/reject`,
    rejectRequestPayload,
  );
  return response.data;
};

// mechanic and admin only method
export const updateServiceRequest = async (
  serviceRequestId: string,
  updateDetails: ServiceRequestUpdatePayload,
): Promise<ServiceRequestResponse> => {
  const response = await axiosClient.patch<ServiceRequestResponse>(
    `/service-requests/${serviceRequestId}`,
    updateDetails,
  );
  return response.data;
};
