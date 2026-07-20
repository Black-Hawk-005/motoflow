import type { ServiceStatus } from "../../types/serviceRequest";

interface StatusBadgeProps {
  status: ServiceStatus;
}

export const StatusBadge = ({ status }: StatusBadgeProps) => (
  <span className={`badge-${status}`}>{status.replace("_", " ")}</span>
);
