import { useVehicles } from "../hooks/useVehicles";
import { useCreateVehicle } from "../hooks/useCreateVehicle";
import { useState } from "react";
import type { SubmitEvent } from "react";

export const CustomerPage = () => {
  const { data, isLoading, isError: isListError } = useVehicles();
  const { mutate, isPending, isError: isCreateError } = useCreateVehicle();

  const [make, setMake] = useState<string>("");
  const [model, setModel] = useState<string>("");
  const [year, setYear] = useState<number>(1886);
  const [license_plate, setLicensePlate] = useState<string>("");

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    mutate(
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
    <>
      <h1>Customer</h1>
      {isLoading && <p>Loading...</p>}

      {isListError && <p>Something went wrong</p>}

      {data?.map((vehicle) => (
        <div key={vehicle.id}>
          {vehicle.make} - {vehicle.model}({vehicle.year}){" "}
          {vehicle.license_plate}
        </div>
      ))}

      <form onSubmit={(e) => handleSubmit(e)}>
        <label htmlFor="make-input">Make:</label>
        <input
          id="make-input"
          type="text"
          value={make}
          onChange={(e) => setMake(e.target.value)}
        />
        <label htmlFor="model-input">Model:</label>
        <input
          id="model-input"
          type="text"
          value={model}
          onChange={(e) => setModel(e.target.value)}
        />
        <label htmlFor="year-input">Year:</label>
        <input
          id="year-input"
          type="number"
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
        />
        <label htmlFor="license-plate-input">License Plate:</label>
        <input
          id="license-plate-input"
          value={license_plate}
          type="text"
          onChange={(e) => setLicensePlate(e.target.value)}
        />

        <button type="submit" disabled={isPending}>
          {isPending ? "Adding..." : "Submit"}
        </button>

        {isCreateError && <p>Failed to add vehicle</p>}
      </form>
    </>
  );
};
