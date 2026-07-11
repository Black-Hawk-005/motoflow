import { useVehicles } from "../../hooks/useVehicles";

export const VehicleList = () => {
  const {
    data: vehicles,
    isLoading: isVLoading,
    isError: isListError,
  } = useVehicles();
  return (
    <div id="vehicle-list">
      <h2>Vehicles</h2>
      {isVLoading && <p>Loading...</p>}

      {isListError && <p>Something went wrong</p>}

      {vehicles?.map((vehicle) => (
        <div key={vehicle.id}>
          {vehicle.make} - {vehicle.model}({vehicle.year}){" "}
          {vehicle.license_plate}
        </div>
      ))}
    </div>
  );
};
