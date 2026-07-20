import { useState } from "react";
import type { SubmitEvent } from "react";

import { useCreateComment } from "../../hooks/comment/useCreateComment";
import { extractErrorMessage } from "../../utils/error";

interface CreateCommentFormProps {
  id: string;
}

export const CreateCommentForm = ({ id }: CreateCommentFormProps) => {
  const {
    mutate: createComment,
    isPending: isCPending,
    isError: isCError,
    error: createCommentError,
  } = useCreateComment();

  const [message, setMessage] = useState("");

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    createComment(
      {
        service_request_id: id,
        message,
      },
      {
        onSuccess: () => setMessage(""),
      },
    );
  };

  return (
    <form onSubmit={(e) => handleSubmit(e)} className="mt-3 flex items-center gap-3">
      <input
        id="message-input"
        placeholder="Write a message..."
        className="field-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        type="text"
      />
      <button type="submit" className="btn-primary shrink-0" disabled={isCPending}>
        {isCPending ? "Sending..." : "Send"}
      </button>
      {isCError && <p className="error-text">{extractErrorMessage(createCommentError)}</p>}
    </form>
  );
};
