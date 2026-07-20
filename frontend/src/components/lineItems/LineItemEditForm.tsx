import { useState, type SubmitEvent } from "react";

import { useUpdateLineItem } from "../../hooks/lineItem/useUpdateLineItem";
import { useDeleteLineItem } from "../../hooks/lineItem/useDeleteLineItem";
import type { ServiceLineItemResponse } from "../../types/serviceLineItem";
import { extractErrorMessage } from "../../utils/error";

interface LineItemEditFormProps {
  lineItem: ServiceLineItemResponse;
}

export const LineItemEditForm = (props: LineItemEditFormProps) => {
  const [draftDescription, setDraftDescription] = useState(
    props.lineItem.description,
  );
  const [draftCost, setDraftCost] = useState(props.lineItem.cost);

  const {
    mutate: updateLI,
    isPending: isULPending,
    isError: isULError,
    error: updateLIError,
  } = useUpdateLineItem();
  const {
    mutate: deleteLI,
    isPending: isDLPending,
    isError: isDLError,
    error: deleteLIError,
  } = useDeleteLineItem();

  const handleLineItemUpdate = (
    e: SubmitEvent<HTMLFormElement>,
    lineItemId: string,
  ) => {
    e.preventDefault();
    updateLI({
      id: lineItemId,
      updateDetails: {
        description: draftDescription,
        cost: draftCost,
      },
    });
  };

  return (
    <form
      id={`line-item-${props.lineItem.id}`}
      onSubmit={(e) => handleLineItemUpdate(e, props.lineItem.id)}
      className="flex flex-wrap items-center gap-2"
    >
      <input
        type="text"
        className="field-input flex-1"
        value={draftDescription}
        onChange={(e) => setDraftDescription(e.target.value)}
      />
      <input
        type="text"
        className="field-input w-24"
        value={draftCost}
        onChange={(e) => setDraftCost(e.target.value)}
      />
      <button type="submit" className="btn-secondary" disabled={isULPending}>
        Update
      </button>
      <button
        type="button"
        className="btn-danger"
        disabled={isDLPending}
        onClick={() =>
          deleteLI({
            lineItemId: props.lineItem.id,
            serviceRequestId: props.lineItem.service_request_id,
          })
        }
      >
        Delete
      </button>
      {isULError && <p className="error-text w-full">{extractErrorMessage(updateLIError)}</p>}
      {isDLError && <p className="error-text w-full">{extractErrorMessage(deleteLIError)}</p>}
    </form>
  );
};
