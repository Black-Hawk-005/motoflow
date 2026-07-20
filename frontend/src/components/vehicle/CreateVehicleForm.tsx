import { useState } from "react";
import type { SubmitEvent } from "react";

import { useCreateVehicle } from "../../hooks/vehicle/useCreateVehicle";
import { extractErrorMessage } from "../../utils/error";

export const CreateVehicleForm = () => {
  const {
    mutate: createVehicle,
    isPending: isVPending,
    isError: isCreateError,
    error: createVehicleError,
  } = useCreateVehicle();

  const [make, setMake] = useState<string>("");
  const [model, setModel] = useState<string>("");
  const [year, setYear] = useState<number>(1886);
  const [license_plate, setLicensePlate] = useState<string>("");

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    createVehicle(
      { make, model, year, license_plate },
      {
        onSuccess: () => {
          setMake("");
          setModel("");
          setYear(1896);
          setLicensePlate("");
        },
      },
    );
  };

  return (
    <form
      onSubmit={(e) => handleSubmit(e)}
      className="grid grid-cols-2 gap-4 border-t border-slate-100 pt-4 sm:grid-cols-4"
    >
      <div>
        <label htmlFor="make-input" className="field-label">
          Make
        </label>
        <input
          id="make-input"
          type="text"
          className="field-input"
          value={make}
          onChange={(e) => setMake(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="model-input" className="field-label">
          Model
        </label>
        <input
          id="model-input"
          type="text"
          className="field-input"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="year-input" className="field-label">
          Year
        </label>
        <input
          id="year-input"
          type="number"
          className="field-input"
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
        />
      </div>
      <div>
        <label htmlFor="license-plate-input" className="field-label">
          License Plate
        </label>
        <input
          id="license-plate-input"
          value={license_plate}
          type="text"
          className="field-input"
          onChange={(e) => setLicensePlate(e.target.value)}
        />
      </div>

      <div className="col-span-2 flex items-end gap-3 sm:col-span-4">
        <button type="submit" className="btn-primary" disabled={isVPending}>
          {isVPending ? "Adding..." : "Add Vehicle"}
        </button>
        {isCreateError && (
          <p className="error-text">{extractErrorMessage(createVehicleError)}</p>
        )}
      </div>
    </form>
  );
};
