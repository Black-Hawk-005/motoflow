import { useState, type SubmitEvent } from "react";
import { useRejectServiceRequest } from "../../hooks/serviceRequest/useRejectServiceRequest";

interface RejectServiceRequestApprovalFormProps {
  id: string;
}

export const RejectServiceRequestApprovalForm = (
  props: RejectServiceRequestApprovalFormProps,
) => {
  const [message, setMessage] = useState("");
  const {
    mutate: rejectSR,
    isPending: isRejectingSR,
    isError: isRejectSRError,
  } = useRejectServiceRequest();
  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    rejectSR(
      {
        id: props.id,
        payload: { message: message },
      },
      { onSuccess: () => setMessage("") },
    );
  };

  return (
    <form onSubmit={(e) => handleSubmit(e)}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button type="submit" disabled={isRejectingSR || !message.trim()}>
        Reject
      </button>
      {isRejectSRError && <p>Failed to reject</p>}
    </form>
  );
};
