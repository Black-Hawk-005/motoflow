import { useMe } from "../../hooks/auth/useMe";
import { useServiceRequest } from "../../hooks/serviceRequest/useServiceRequest";
import { useUpdateServiceRequest } from "../../hooks/serviceRequest/useUpdateServiceRequest";
import type { ServiceStatus } from "../../types/serviceRequest";
import { extractErrorMessage } from "../../utils/error";

export interface UpdateStatusControlProps {
  id: string;
}

export const VALID_TRANSITIONS: Record<ServiceStatus, ServiceStatus[]> = {
  pending: [],
  assigned: ["in_progress"],
  in_progress: ["action_required"],
  approved: ["completed", "in_progress"],
  completed: ["closed"],
  action_required: [],
  closed: [],
};

export const UpdateStatusControl = (props: UpdateStatusControlProps) => {
  const { data: user, isLoading: isRoleLoading } = useMe();
  const {
    mutate: updateServiceRequest,
    isPending: isUpdateSRPending,
    isError: isUpdateSRError,
    error: updateSRError,
  } = useUpdateServiceRequest();
  const { data: serviceRequest, isLoading: isSRLoading } = useServiceRequest(
    props.id,
  );

  if (user?.role !== "mechanic" && user?.role !== "admin") {
    return null;
  }

  if (isRoleLoading || isSRLoading || !serviceRequest) {
    return null;
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      {VALID_TRANSITIONS[serviceRequest.status].map((status) => (
        <button
          key={status}
          className="btn-secondary capitalize"
          disabled={isUpdateSRPending}
          onClick={() =>
            updateServiceRequest({ id: props.id, payload: { status } })
          }
        >
          Mark as {status.replace("_", " ")}
        </button>
      ))}
      {isUpdateSRError && (
        <p className="error-text">{extractErrorMessage(updateSRError)}</p>
      )}
    </div>
  );
};
