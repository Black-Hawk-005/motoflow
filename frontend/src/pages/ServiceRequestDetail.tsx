import { useParams } from "react-router-dom";
import { useServiceRequest } from "../hooks/useServiceRequest";
import { useMe } from "../hooks/useMe";
import { useLineItems } from "../hooks/useLineItems";
import { useComments } from "../hooks/useComments";
import { useCreateComment } from "../hooks/useCreateComment";
import { useApproveLineItem } from "../hooks/useApproveLineItem";
import { useState } from "react";
import type { SubmitEvent } from "react";

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
      <ul>
        {comments?.map((comment) => (
          <li key={comment.id}>
            {" "}
            {comment.author_id} - {comment.message}{" "}
          </li>
        ))}
      </ul>
    </>
  );
};

export default ServiceRequestDetail;
