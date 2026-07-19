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
      {isCPending && <p>Loading...</p>}
      {isCError && <p>{extractErrorMessage(createCommentError)}</p>}
    </form>
  );
};
