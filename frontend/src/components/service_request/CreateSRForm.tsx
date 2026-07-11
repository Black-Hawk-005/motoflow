import type { SubmitEvent } from "react";
import { useState } from "react";

import { useCreateServiceRequest } from "../../hooks/useCreateServiceRequest";
import { useVehicles } from "../../hooks/useVehicles";

export const CreateSRForm = () => {
  const {
    mutate: createSR,
    isPending: isCreatingSR,
    isError: isCreateSRError,
  } = useCreateServiceRequest();
  const {
    data: vehicles,
    isLoading: isVLoading,
    isError: isVListError,
  } = useVehicles();

  const [selectedVehicleId, setSelectedVehicleId] = useState<string>("");
  const [complaint, setComplaint] = useState<string>("");

  const handleCreateSR = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    createSR(
      { vehicle_id: selectedVehicleId, initial_complaint: complaint },
      {
        onSuccess: () => {
          setSelectedVehicleId("");
          setComplaint("");
        },
      },
    );
  };

  return (
    <form onSubmit={(e) => handleCreateSR(e)}>
      <label htmlFor="vehicle-select">Vehicle:</label>
      {isVLoading && <p>Vehicle list loading</p>}
      {!isVLoading && (
        <select
          id="vehicle-select"
          value={selectedVehicleId}
          onChange={(e) => setSelectedVehicleId(e.target.value)}
        >
          <option value="" disabled>
            Select a vehicle
          </option>
          {vehicles?.map((vehicle) => (
            <option key={vehicle.id} value={vehicle.id}>
              {vehicle.make} {vehicle.model} ({vehicle.license_plate})
            </option>
          ))}
        </select>
      )}
      {isVListError && <p>Failed to fetch vehicle list</p>}

      <label htmlFor="complaint-input">Complaint:</label>
      <textarea
        id="complaint-input"
        value={complaint}
        onChange={(e) => setComplaint(e.target.value)}
      />

      <button type="submit" disabled={isCreatingSR || !selectedVehicleId}>
        {isCreatingSR ? "Submitting..." : "Submit"}
      </button>

      {isCreateSRError && <p>Failed to create service request</p>}
    </form>
  );
};
