import { Link } from "react-router-dom";

import { useServiceRequests } from "../../hooks/serviceRequest/useServiceRequests";
import { extractErrorMessage } from "../../utils/error";

export const ServiceRequestList = () => {
  const {
    data: serviceRequests,
    isLoading: isSRLoading,
    isError: isSRListError,
    error: srListError,
  } = useServiceRequests();

  return (
    <div>
      <h2>Service Requests</h2>
      {isSRLoading && <p>Loading...</p>}

      {isSRListError && <p>{extractErrorMessage(srListError)}</p>}

      {serviceRequests?.map((sr) => (
        <div key={sr.id}>
          <Link to={`/service-request/${sr.id}`}>
            [{sr.status}] {sr.initial_complaint}
          </Link>
        </div>
      ))}
    </div>
  );
};
