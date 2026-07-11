import { useLineItems } from "../../hooks/lineItem/useLineItems";
import { useApproveLineItem } from "../../hooks/lineItem/useApproveLineItem";
import { useMe } from "../../hooks/auth/useMe";

interface LineItemsListProps {
  id: string;
}

export const LineItemsList = (props: LineItemsListProps) => {
  const { data: lineItems, isLoading: isLILoading } = useLineItems(props.id);
  const { data: user, isLoading: isRoleLoading } = useMe();
  const {
    mutate: approveLI,
    isPending: isALPending,
    isError: isALError,
  } = useApproveLineItem();

  return (
    <div>
      <h3>Line Items: </h3>
      {isLILoading || isRoleLoading ? (
        <p>Line items are loading...</p>
      ) : (
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
      )}
    </div>
  );
};
