export type ServiceStatus =
  | "pending"
  | "assigned"
  | "in_progress"
  | "action_required"
  | "approved"
  | "completed"
  | "closed";

export interface ServiceRequestResponse {
  id: string;
  customer_id: string;
  vehicle_id: string;
  mechanic_id: string | null | undefined;
  initial_complaint: string;
  status: ServiceStatus;
  created_at: string;
  updated_at: string;
}

export interface ServiceRequestCreatePayload {
  vehicle_id: string;
  initial_complaint: string;
}

export interface ServiceRequestUpdatePayload {
  mechanic_id?: string;
  status?: ServiceStatus;
}

export interface ServiceRequestRejectPayload {
  message: string;
}
