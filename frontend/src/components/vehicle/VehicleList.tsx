import { useVehicles } from "../../hooks/vehicle/useVehicles";
import { extractErrorMessage } from "../../utils/error";

export const VehicleList = () => {
  const {
    data: vehicles,
    isLoading: isVLoading,
    isError: isListError,
    error: vehiclesError,
  } = useVehicles();
  return (
    <div id="vehicle-list">
      <h2>Vehicles</h2>
      {isVLoading && <p>Loading...</p>}

      {isListError && <p>{extractErrorMessage(vehiclesError)}</p>}

      {vehicles?.map((vehicle) => (
        <div key={vehicle.id}>
          {vehicle.make} - {vehicle.model}({vehicle.year}){" "}
          {vehicle.license_plate}
        </div>
      ))}
    </div>
  );
};
