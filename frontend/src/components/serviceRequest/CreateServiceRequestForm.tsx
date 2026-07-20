import type { SubmitEvent } from "react";
import { useState } from "react";

import { useCreateServiceRequest } from "../../hooks/serviceRequest/useCreateServiceRequest";
import { useVehicles } from "../../hooks/vehicle/useVehicles";
import { extractErrorMessage } from "../../utils/error";

export const CreateServiceRequestForm = () => {
  const {
    mutate: createSR,
    isPending: isCreatingSR,
    isError: isCreateSRError,
    error: createSRError,
  } = useCreateServiceRequest();
  const {
    data: vehicles,
    isLoading: isVLoading,
    isError: isVListError,
    error: vListError,
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
    <form
      onSubmit={(e) => handleCreateSR(e)}
      className="space-y-4 border-t border-slate-100 pt-4"
    >
      <div>
        <label htmlFor="vehicle-select" className="field-label">
          Vehicle
        </label>
        {isVLoading && <p className="helper-text">Vehicle list loading</p>}
        {!isVLoading && (
          <select
            id="vehicle-select"
            className="field-input"
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
        {isVListError && <p className="error-text">{extractErrorMessage(vListError)}</p>}
      </div>

      <div>
        <label htmlFor="complaint-input" className="field-label">
          Complaint
        </label>
        <textarea
          id="complaint-input"
          className="field-input"
          value={complaint}
          onChange={(e) => setComplaint(e.target.value)}
        />
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          className="btn-primary"
          disabled={isCreatingSR || !selectedVehicleId}
        >
          {isCreatingSR ? "Submitting..." : "Create Service Request"}
        </button>
        {isCreateSRError && (
          <p className="error-text">{extractErrorMessage(createSRError)}</p>
        )}
      </div>
    </form>
  );
};
