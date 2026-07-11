import { VehicleList } from "../components/vehicles/VehicleList";
import { CreateVehicleForm } from "../components/vehicles/CreateVehicleForm";
import { ServiceRequestList } from "../components/service_request/ServiceRequestList";
import { CreateSRForm } from "../components/service_request/CreateSRForm";

export const CustomerPage = () => {
  return (
    <>
      <h1>Customer</h1>

      {/* Vehicle section */}
      <VehicleList />

      {/* Add vehicle section */}
      <CreateVehicleForm />

      {/* Service request section */}
      <ServiceRequestList />

      {/* Create service request form */}
      <CreateSRForm />
    </>
  );
};
