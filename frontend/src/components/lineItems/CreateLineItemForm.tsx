import { type SubmitEvent, useState } from "react";

import { useMe } from "../../hooks/auth/useMe";
import { useCreateLineItem } from "../../hooks/lineItem/useCreateLineItem";

interface CreateLineItemProps {
  id: string;
}

export const CreateLineItemForm = (props: CreateLineItemProps) => {
  const {
    mutate: createLineItem,
    isPending: isLIPending,
    isError: isLIError,
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
    <>
      <h4>Create Line Item:</h4>
      <form onSubmit={(e) => handleSubmit(e)}>
        <label htmlFor="line-item-description-input">Description</label>
        <textarea
          id="line-item-description-input"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        ></textarea>

        <label htmlFor="line-item-cost-input">Cost</label>
        <input
          id="line-item-cost-input"
          type="number"
          value={cost}
          onChange={(e) => setCost(e.target.value)}
        ></input>

        <button disabled={isLIPending} type="submit">
          Create
        </button>
      </form>
      {isLIError && <p>Failed to create line item</p>}
    </>
  );
};
