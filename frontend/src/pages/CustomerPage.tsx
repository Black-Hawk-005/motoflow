import { VehicleList } from "../components/vehicle/VehicleList";
import { CreateVehicleForm } from "../components/vehicle/CreateVehicleForm";
import { ServiceRequestList } from "../components/serviceRequest/ServiceRequestList";
import { CreateServiceRequestForm } from "../components/serviceRequest/CreateServiceRequestForm";

export const CustomerPage = () => {
  return (
    <div className="space-y-5">
      <h1 className="page-title">Customer</h1>

      <section className="card space-y-3">
        <VehicleList />
        <CreateVehicleForm />
      </section>

      <section className="card space-y-3">
        <ServiceRequestList />
        <CreateServiceRequestForm />
      </section>
    </div>
  );
};
