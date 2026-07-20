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
      <h2 className="section-title mb-3">Vehicles</h2>
      {isVLoading && <p className="helper-text">Loading...</p>}

      {isListError && <p className="error-text">{extractErrorMessage(vehiclesError)}</p>}

      {!isVLoading && vehicles?.length === 0 && (
        <p className="helper-text">No vehicles yet.</p>
      )}

      <ul className="divide-y divide-slate-100">
        {vehicles?.map((vehicle) => (
          <li key={vehicle.id} className="py-2 text-sm text-slate-700">
            <span className="font-medium">
              {vehicle.make} {vehicle.model}
            </span>{" "}
            <span className="text-slate-400">({vehicle.year})</span>{" "}
            <span className="text-slate-500">{vehicle.license_plate}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
