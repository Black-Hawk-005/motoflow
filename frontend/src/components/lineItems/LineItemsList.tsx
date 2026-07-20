import { useLineItems } from "../../hooks/lineItem/useLineItems";
import { useApproveLineItem } from "../../hooks/lineItem/useApproveLineItem";
import { useMe } from "../../hooks/auth/useMe";

import { LineItemEditForm } from "./LineItemEditForm";
import { useServiceRequest } from "../../hooks/serviceRequest/useServiceRequest";
import { extractErrorMessage } from "../../utils/error";

interface LineItemsListProps {
  id: string;
}

export const LineItemsList = (props: LineItemsListProps) => {
  const { data: lineItems, isLoading: isLILoading } = useLineItems(props.id);
  const { data: user, isLoading: isRoleLoading } = useMe();
  const { data: serviceRequest, isLoading: isSRLoading } = useServiceRequest(
    props.id,
  );
  const isLocked =
    !isSRLoading &&
    serviceRequest &&
    ["approved", "completed", "closed"].includes(serviceRequest.status);

  const {
    mutate: approveLI,
    isPending: isALPending,
    isError: isALError,
    error: approveLIError,
  } = useApproveLineItem();

  return (
    <div>
      <h3 className="section-title mb-3">Line Items</h3>
      {isLILoading || isRoleLoading ? (
        <p className="helper-text">Line items are loading...</p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {lineItems?.length === 0 && (
            <p className="helper-text">No line items yet.</p>
          )}
          {lineItems?.map((lineItem) => (
            <li key={lineItem.id} className="space-y-2 py-3">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="text-slate-700">
                  {lineItem.description}{" "}
                  <span className="text-slate-400">${lineItem.cost}</span>
                </span>
                <span
                  className={
                    lineItem.is_approved
                      ? "badge-approved"
                      : "badge-pending"
                  }
                >
                  {lineItem.is_approved ? "Approved" : "Pending"}
                </span>
              </div>
              {user?.role === "customer" &&
                !lineItem.is_approved &&
                !isLocked && (
                  <button
                    className="btn-secondary"
                    disabled={isALPending}
                    onClick={() => approveLI(lineItem.id)}
                  >
                    Approve
                  </button>
                )}
              {isALError && <p className="error-text">{extractErrorMessage(approveLIError)}</p>}
              {user?.role === "mechanic" && !isLocked && (
                <LineItemEditForm lineItem={lineItem} />
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
