import { useParams } from "react-router-dom";

import { useServiceRequest } from "../hooks/serviceRequest/useServiceRequest";
import { useVehicle } from "../hooks/vehicle/useVehicle";
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
import { formatDateTime } from "../utils/date";

const ServiceRequestDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { data: serviceRequest, isLoading: isSRLoading } = useServiceRequest(
    id as string,
  );
  const { data: vehicleDetails, isLoading: isVLoading } = useVehicle(
    serviceRequest?.vehicle_id,
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

      <div className="card space-y-4">
        <p className="text-slate-700">{serviceRequest?.initial_complaint}</p>
        <div className="grid grid-cols-2 gap-4 border-t border-slate-100 pt-4 sm:grid-cols-3">
          <div>
            <p className="info-label">Created</p>
            <p className="info-value">
              {serviceRequest && formatDateTime(serviceRequest.created_at)}
            </p>
          </div>
          <div>
            <p className="info-label">Last Updated</p>
            <p className="info-value">
              {serviceRequest && formatDateTime(serviceRequest.updated_at)}
            </p>
          </div>
          {(user?.role === "admin" || user?.role === "customer") && (
            <div>
              <p className="info-label">Assigned Mechanic</p>
              <p className="info-value">
                {serviceRequest?.mechanic?.full_name ?? "Unassigned"}
              </p>
            </div>
          )}
          {(user?.role === "admin" || user?.role === "mechanic") &&
            serviceRequest?.customer && (
              <div className="col-span-2 sm:col-span-3">
                <p className="info-label">Customer Contact</p>
                <p className="info-value">
                  {serviceRequest.customer.full_name}
                  <span className="mx-2 text-slate-300">·</span>
                  {serviceRequest.customer.phone}
                  <span className="mx-2 text-slate-300">·</span>
                  {serviceRequest.customer.email}
                </p>
              </div>
            )}
        </div>
      </div>

      <div className="card space-y-3">
        <h3 className="section-title">Vehicle Details</h3>
        {isVLoading ? (
          <p className="helper-text">Loading...</p>
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div>
              <p className="info-label">Make</p>
              <p className="info-value">{vehicleDetails?.make}</p>
            </div>
            <div>
              <p className="info-label">Model</p>
              <p className="info-value">
                {vehicleDetails?.model} ({vehicleDetails?.year})
              </p>
            </div>
            <div>
              <p className="info-label">License Plate</p>
              <p className="info-value">{vehicleDetails?.license_plate}</p>
            </div>
          </div>
        )}
      </div>

      {hasActions && (
        <div className="card space-y-4">
          {user?.role === "admin" && serviceRequest?.status === "pending" && (
            <div className="alert-warning">
              <svg
                className="h-5 w-5 shrink-0"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.63-1.516 2.63H3.72c-1.347 0-2.189-1.463-1.515-2.63L8.485 2.495ZM10 6a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 10 6Zm0 8a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"
                  clipRule="evenodd"
                />
              </svg>
              <span>This request hasn't been assigned to a mechanic yet.</span>
            </div>
          )}
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
