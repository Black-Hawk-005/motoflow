import { useState, type SubmitEvent } from "react";

import { useUpdateLineItem } from "../../hooks/lineItem/useUpdateLineItem";
import { useDeleteLineItem } from "../../hooks/lineItem/useDeleteLineItem";
import type { ServiceLineItemResponse } from "../../types/serviceLineItem";

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
  } = useUpdateLineItem();
  const {
    mutate: deleteLI,
    isPending: isDLPending,
    isError: isDLError,
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
    >
      <input
        type="text"
        value={draftDescription}
        onChange={(e) => setDraftDescription(e.target.value)}
      />
      <input
        type="text"
        value={draftCost}
        onChange={(e) => setDraftCost(e.target.value)}
      />
      <button type="submit" disabled={isULPending}>
        Update
      </button>
      {isULError && <p>Line Item update failed</p>}
      <button
        type="button"
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
      {isDLError && <p>Failed to delete line item</p>}
    </form>
  );
};
