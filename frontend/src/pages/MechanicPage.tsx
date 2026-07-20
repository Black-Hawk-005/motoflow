import { ServiceRequestList } from "../components/serviceRequest/ServiceRequestList";

export const MechanicPage = () => {
  return (
    <div className="space-y-8">
      <h1 className="page-title">My Assigned Requests</h1>
      <section className="card">
        <ServiceRequestList />
      </section>
    </div>
  );
};
