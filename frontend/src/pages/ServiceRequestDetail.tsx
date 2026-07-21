import { useParams } from "react-router-dom";

import { useServiceRequest } from "../hooks/serviceRequest/useServiceRequest";
import { useMe } from "../hooks/auth/useMe";
import { useApproveServiceRequest } from "../hooks/serviceRequest/useApproveServiceRequest";

import { LineItemsList } from "../components/lineItems/LineItemsList";
import { CommentList } from "../components/comments/CommentList";
import { CreateCommentForm } from "../components/comments/CreateCommentForm";
import { CreateLineItemForm } from "../components/lineItems/CreateLineItemForm";
import { UpdateStatusControl } from "../components/serviceRequest/updateStatusControl";
import { RejectServiceRequestApprovalForm } from "../components/serviceRequest/RejectServiceRequestApprovalForm";
import { AssignMechanicControl } from "../components/serviceRequest/AssignMechanicControl";
import type { ServiceStatus } from "../types/serviceRequest";
import { extractErrorMessage } from "../utils/error";
import { StatusBadge } from "../components/common/StatusBadge";
import { VALID_TRANSITIONS } from "../components/serviceRequest/updateStatusControl";

const ServiceRequestDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { data: serviceRequest, isLoading: isSRLoading } = useServiceRequest(
    id as string,
  );
  const { data: user, isLoading: isRoleLoading } = useMe();
  const {
    mutate: approveSR,
    isPending: isApprovingSR,
    isError: isApproveSRError,
    error: approveSRError,
  } = useApproveServiceRequest();

  const canApproveOrReject =
    user?.role === "customer" && serviceRequest?.status === "action_required";
  const canUpdateStatus =
    (user?.role === "mechanic" || user?.role === "admin") &&
    !!serviceRequest &&
    VALID_TRANSITIONS[serviceRequest.status].length > 0;
  const canAssignMechanic = user?.role === "admin";

  const hasActions = canApproveOrReject || canUpdateStatus || canAssignMechanic;

  if (isSRLoading || isRoleLoading) {
    return <p className="helper-text">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Service Request Details</h1>
        {serviceRequest && <StatusBadge status={serviceRequest.status} />}
      </div>

      <div className="card space-y-2">
        <p className="text-slate-700">{serviceRequest?.initial_complaint}</p>
        <p className="helper-text">Created at: {serviceRequest?.created_at}</p>
        {user?.role === "admin" && (
          <p className="helper-text">
            Assigned mechanic id: {serviceRequest?.mechanic_id ?? "—"}
          </p>
        )}
      </div>

      {hasActions && (
        <div className="card space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            {user?.role === "customer" &&
              serviceRequest?.status === "action_required" && (
                <button
                  className="btn-primary"
                  disabled={isApprovingSR}
                  onClick={() => approveSR(serviceRequest.id)}
                >
                  Approve
                </button>
              )}
            <UpdateStatusControl id={id as string} />
          </div>

          {user?.role === "admin" && (
            <AssignMechanicControl
              serviceRequestId={serviceRequest?.id as string}
              mechanicId={serviceRequest?.mechanic_id as string}
              status={serviceRequest?.status as ServiceStatus}
            />
          )}

          {user?.role === "customer" &&
            serviceRequest?.status === "action_required" && (
              <RejectServiceRequestApprovalForm id={id as string} />
            )}

          {isApproveSRError && (
            <p className="error-text">{extractErrorMessage(approveSRError)}</p>
          )}
        </div>
      )}

      <div className="card space-y-2">
        <LineItemsList id={id as string} />
        <CreateLineItemForm id={id as string} />
      </div>

      <div className="card">
        <h3 className="section-title mb-3">Messages</h3>
        <CommentList id={id as string} />
        <CreateCommentForm id={id as string} />
      </div>
    </div>
  );
};

export default ServiceRequestDetail;
