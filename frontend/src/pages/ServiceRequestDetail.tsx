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

  if (isSRLoading || isRoleLoading) {
    return <p>Loading...</p>;
  }

  return (
    <>
      <h1>Service Request Details</h1>

      <h2>Status: {serviceRequest?.status}</h2>
      {user?.role === "customer" &&
        serviceRequest?.status === "action_required" && (
          <button
            disabled={isApprovingSR}
            onClick={() => approveSR(serviceRequest.id)}
          >
            Approve
          </button>
        )}
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

      {isApproveSRError && <p>{extractErrorMessage(approveSRError)}</p>}

      <UpdateStatusControl id={id as string} />

      <p>Initial Complaint</p>
      <p>{serviceRequest?.initial_complaint}</p>
      <p>Created at: {serviceRequest?.created_at}</p>
      {user?.role === "admin" && (
        <p>Assigned mechanic id: {serviceRequest?.mechanic_id}</p>
      )}
      <LineItemsList id={id as string} />
      <CreateLineItemForm id={id as string} />

      <h3>Messages:</h3>
      <CommentList id={id as string} />
      <CreateCommentForm id={id as string} />
    </>
  );
};

export default ServiceRequestDetail;
