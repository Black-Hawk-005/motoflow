import { type SubmitEvent, useState } from "react";

import { useMe } from "../../hooks/auth/useMe";
import { useCreateLineItem } from "../../hooks/lineItem/useCreateLineItem";
import { extractErrorMessage } from "../../utils/error";

interface CreateLineItemProps {
  id: string;
}

export const CreateLineItemForm = (props: CreateLineItemProps) => {
  const {
    mutate: createLineItem,
    isPending: isLIPending,
    isError: isLIError,
    error: createLIError,
  } = useCreateLineItem();
  const { data: user } = useMe();

  const [description, setDescription] = useState("");
  const [cost, setCost] = useState("0");

  if (user?.role !== "mechanic") return null;

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    createLineItem(
      {
        service_request_id: props.id,
        description: description,
        cost: cost,
      },
      {
        onSuccess: () => {
          setDescription("");
          setCost("0");
        },
      },
    );
  };

  return (
    <div className="border-t border-slate-100 pt-4">
      <h4 className="field-label">Add Line Item</h4>
      <form onSubmit={(e) => handleSubmit(e)} className="flex flex-wrap items-end gap-3">
        <div className="flex-1">
          <label htmlFor="line-item-description-input" className="field-label">
            Description
          </label>
          <textarea
            id="line-item-description-input"
            className="field-input"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          ></textarea>
        </div>

        <div className="w-28">
          <label htmlFor="line-item-cost-input" className="field-label">
            Cost
          </label>
          <input
            id="line-item-cost-input"
            type="number"
            className="field-input"
            value={cost}
            onChange={(e) => setCost(e.target.value)}
          ></input>
        </div>

        <button className="btn-primary" disabled={isLIPending} type="submit">
          Add
        </button>
      </form>
      {isLIError && <p className="error-text mt-2">{extractErrorMessage(createLIError)}</p>}
    </div>
  );
};
