import axiosClient from "./client";
import type {
  ServiceLineItemCreatePayload,
  ServiceLineItemResponse,
} from "../types/serviceLineItem";

export const create_line_item = async (
  line_item_details: ServiceLineItemCreatePayload,
): Promise<ServiceLineItemResponse> => {
  const response = await axiosClient.post<ServiceLineItemResponse>(
    "/line-items/",
    line_item_details,
  );
  return response.data;
};

export const list_line_items = async (
  service_request_id: string,
): Promise<ServiceLineItemResponse[]> => {
  const response = await axiosClient.get<ServiceLineItemResponse[]>(
    `/line-items/${service_request_id}`,
  );
  return response.data;
};

export const approve_line_item = async (
  line_item_id: string,
): Promise<ServiceLineItemResponse> => {
  const response = await axiosClient.patch<ServiceLineItemResponse>(
    `/line-items/${line_item_id}/approve`,
  );
  return response.data;
};
