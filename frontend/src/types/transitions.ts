import type { ServiceStatus } from "./serviceRequest";

export const VALID_TRANSITIONS: Record<ServiceStatus, ServiceStatus[]> = {
  pending: [],
  assigned: ["in_progress"],
  in_progress: ["action_required"],
  approved: ["completed", "in_progress"],
  completed: ["closed"],
  action_required: [],
  closed: [],
};
