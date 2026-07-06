export interface ServiceLineItemCreatePayload {
  service_request_id: string;
  description: string;
  cost: string;
}

export interface ServiceLineItemResponse {
  id: string;
  service_request_id: string;
  description: string;
  cost: string;
  is_approved: boolean;
}
