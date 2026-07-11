import { Link } from "react-router-dom";

import { useServiceRequests } from "../../hooks/useServiceRequests";

export const ServiceRequestList = () => {
  const {
    data: serviceRequests,
    isLoading: isSRLoading,
    isError: isSRListError,
  } = useServiceRequests();

  return (
    <div>
      <h2>Service Requests</h2>
      {isSRLoading && <p>Loading...</p>}

      {isSRListError && <p>Something went wrong</p>}

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
