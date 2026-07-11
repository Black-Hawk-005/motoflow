import { useParams } from "react-router-dom";
import { useState } from "react";
import type { SubmitEvent } from "react";

import { useServiceRequest } from "../hooks/serviceRequest/useServiceRequest";
import { useMe } from "../hooks/auth/useMe";
import { useLineItems } from "../hooks/lineItem/useLineItems";
import { useComments } from "../hooks/comment/useComments";
import { useCreateComment } from "../hooks/comment/useCreateComment";
import { useApproveLineItem } from "../hooks/lineItem/useApproveLineItem";
import { useApproveServiceRequest } from "../hooks/serviceRequest/useApproveServiceRequest";

const ServiceRequestDetail = () => {
  const { id: id } = useParams<{ id: string }>();
  const { data: serviceRequest, isLoading: isSRLoading } = useServiceRequest(
    id as string,
  );
  const { data: lineItems, isLoading: isLILoading } = useLineItems(
    id as string,
  );
  const { data: user, isLoading: isRoleLoading } = useMe();
  const { data: comments, isLoading: isCLoading } = useComments(id as string);
  const {
    mutate: createComment,
    isPending: isCPending,
    isError: isCError,
  } = useCreateComment();
  const {
    mutate: approveLI,
    isPending: isALPending,
    isError: isALError,
  } = useApproveLineItem();
  const {
    mutate: approveSR,
    isPending: isApprovingSR,
    isError: isApproveSRError,
  } = useApproveServiceRequest();

  const [message, setMessage] = useState("");

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    createComment(
      {
        service_request_id: id as string,
        message,
      },
      {
        onSuccess: () => setMessage(""),
      },
    );
  };

  if (isSRLoading || isLILoading || isCLoading || isRoleLoading) {
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
      <h3>Line Items: </h3>
      <ul>
        {lineItems?.map((lineItem) => (
          <li key={lineItem.id}>
            {lineItem.description} - ${lineItem.cost} -{" "}
            {lineItem.is_approved ? "Approved" : "Pending"}
            {user?.role === "customer" && !lineItem.is_approved && (
              <button
                disabled={isALPending}
                onClick={() => approveLI(lineItem.id)}
              >
                Approve
              </button>
            )}
            {isALError && <p>Failed to approve</p>}
          </li>
        ))}
      </ul>

      <h3>Messages:</h3>
      {isCPending && <p>Loading...</p>}
      {isCError && <p>Failed to add comment</p>}
      <ul>
        {[...(comments ?? [])]
          .sort(
            (a, b) =>
              new Date(a.created_at).getTime() -
              new Date(b.created_at).getTime(),
          )
          .map((comment) => (
            <li key={comment.id}>
              {" "}
              {comment.author.full_name}
              {["mechanic", "admin"].includes(comment.author.role) &&
                ` (${comment.author.role})`}{" "}
              - {comment.message}{" "}
            </li>
          ))}
      </ul>
      <form onSubmit={(e) => handleSubmit(e)}>
        <label htmlFor="message-input">Message: </label>
        <input
          id="message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          type="text"
        />
        <button type="submit" disabled={isCPending}>
          Send
        </button>
      </form>
    </>
  );
};

export default ServiceRequestDetail;
