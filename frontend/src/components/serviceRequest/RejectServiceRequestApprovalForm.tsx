import { useState, type SubmitEvent } from "react";
import { useRejectServiceRequest } from "../../hooks/serviceRequest/useRejectServiceRequest";
import { extractErrorMessage } from "../../utils/error";

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
    error: rejectSRError,
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
    <form onSubmit={(e) => handleSubmit(e)} className="flex items-start gap-3">
      <input
        type="text"
        placeholder="Reason for rejection"
        className="field-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button
        type="submit"
        className="btn-danger shrink-0"
        disabled={isRejectingSR || !message.trim()}
      >
        Reject
      </button>
      {isRejectSRError && <p className="error-text">{extractErrorMessage(rejectSRError)}</p>}
    </form>
  );
};
