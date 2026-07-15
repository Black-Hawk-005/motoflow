import axiosClient from "./client";
import type {
  ServiceLineItemCreatePayload,
  ServiceLineItemResponse,
  ServiceLineItemUpdatePayload,
} from "../types/serviceLineItem";

export const createLineItem = async (
  lineItemDetails: ServiceLineItemCreatePayload,
): Promise<ServiceLineItemResponse> => {
  const response = await axiosClient.post<ServiceLineItemResponse>(
    "/line-items/",
    lineItemDetails,
  );
  return response.data;
};

export const listLineItems = async (
  serviceRequestId: string,
): Promise<ServiceLineItemResponse[]> => {
  const response = await axiosClient.get<ServiceLineItemResponse[]>(
    "/line-items/",
    {
      params: { service_request_id: serviceRequestId },
    },
  );

  return response.data;
};

export const updateLineItem = async (
  lineItemId: string,
  lineItemUpdateDetails: ServiceLineItemUpdatePayload,
): Promise<ServiceLineItemResponse> => {
  const response = await axiosClient.patch<ServiceLineItemResponse>(
    `/line-items/${lineItemId}`,
    lineItemUpdateDetails,
  );
  return response.data;
};

export const approveLineItem = async (
  lineItemId: string,
): Promise<ServiceLineItemResponse> => {
  const response = await axiosClient.patch<ServiceLineItemResponse>(
    `/line-items/${lineItemId}/approve`,
  );
  return response.data;
};

export const deleteLineItem = async (lineItemId: string): Promise<void> => {
  await axiosClient.delete(`/line-items/${lineItemId}`);
};
