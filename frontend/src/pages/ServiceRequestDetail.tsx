import { useParams } from "react-router-dom";

import { useServiceRequest } from "../hooks/serviceRequest/useServiceRequest";
import { useMe } from "../hooks/auth/useMe";
import { useApproveServiceRequest } from "../hooks/serviceRequest/useApproveServiceRequest";
import { LineItemsList } from "../components/lineItems/LineItemsList";
import { CommentList } from "../components/comments/CommentList";
import { CreateCommentForm } from "../components/comments/CreateCommentForm";

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
      {isApproveSRError && <p>Failed to approve service request</p>}
      <p>Initial Complaint</p>
      <p>{serviceRequest?.initial_complaint}</p>
      <p>Created at: {serviceRequest?.created_at}</p>

      <LineItemsList id={id as string} />

      <h3>Messages:</h3>
      <CommentList id={id as string} />
      <CreateCommentForm id={id as string} />
    </>
  );
};

export default ServiceRequestDetail;
