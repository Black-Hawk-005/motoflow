import { Link } from "react-router-dom";

import { useServiceRequests } from "../../hooks/serviceRequest/useServiceRequests";
import { extractErrorMessage } from "../../utils/error";
import { StatusBadge } from "../common/StatusBadge";

export const ServiceRequestList = () => {
  const {
    data: serviceRequests,
    isLoading: isSRLoading,
    isError: isSRListError,
    error: srListError,
  } = useServiceRequests();

  return (
    <div>
      <h2 className="section-title mb-3">Service Requests</h2>
      {isSRLoading && <p className="helper-text">Loading...</p>}

      {isSRListError && <p className="error-text">{extractErrorMessage(srListError)}</p>}

      {!isSRLoading && serviceRequests?.length === 0 && (
        <p className="helper-text">No service requests yet.</p>
      )}

      <ul className="divide-y divide-slate-100">
        {serviceRequests?.map((sr) => (
          <li key={sr.id} className="py-2">
            <Link
              to={`/service-request/${sr.id}`}
              className="flex items-center justify-between gap-3 text-sm text-slate-700 hover:text-indigo-600"
            >
              <span>{sr.initial_complaint}</span>
              <StatusBadge status={sr.status} />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};
