import { VehicleList } from "../components/vehicle/VehicleList";
import { CreateVehicleForm } from "../components/vehicle/CreateVehicleForm";
import { ServiceRequestList } from "../components/serviceRequest/ServiceRequestList";
import { CreateServiceRequestForm } from "../components/serviceRequest/CreateServiceRequestForm";

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
      <CreateServiceRequestForm />
    </>
  );
};
