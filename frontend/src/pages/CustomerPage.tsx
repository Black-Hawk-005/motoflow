import { Link } from "react-router-dom";
import { useState } from "react";
import type { SubmitEvent } from "react";

import { useVehicles } from "../hooks/useVehicles";
import { useCreateVehicle } from "../hooks/useCreateVehicle";
import { useServiceRequests } from "../hooks/useServiceRequests";
import { useCreateServiceRequest } from "../hooks/useCreateServiceRequest";

export const CustomerPage = () => {
  // vehicle data fetch
  const {
    data: vehicles,
    isLoading: isVLoading,
    isError: isListError,
  } = useVehicles();
  const {
    mutate: createVehicle,
    isPending: isVPending,
    isError: isCreateError,
  } = useCreateVehicle();

  // service requests data fetch
  const {
    data: serviceRequests,
    isLoading: isSRLoading,
    isError: isSRListError,
  } = useServiceRequests();
  const {
    mutate: createSR,
    isPending: isCreatingSR,
    isError: isCreateSRError,
  } = useCreateServiceRequest();

  // states to store create vehicle input values
  const [make, setMake] = useState<string>("");
  const [model, setModel] = useState<string>("");
  const [year, setYear] = useState<number>(1886);
  const [license_plate, setLicensePlate] = useState<string>("");

  // states to store create service request input values
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>("");
  const [complaint, setComplaint] = useState<string>("");

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
    <>
      <h1>Customer</h1>

      {/* Vehicle section */}
      <h2>Vehicles</h2>
      {isVLoading && <p>Loading...</p>}

      {isListError && <p>Something went wrong</p>}

      {vehicles?.map((vehicle) => (
        <div key={vehicle.id}>
          {vehicle.make} - {vehicle.model}({vehicle.year}){" "}
          {vehicle.license_plate}
        </div>
      ))}

      {/* Add vehicle section */}
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

        <button type="submit" disabled={isVPending}>
          {isVPending ? "Adding..." : "Submit"}
        </button>

        {isCreateError && <p>Failed to add vehicle</p>}
      </form>

      {/* Service request section */}
      <h2>Service Requests</h2>
      {isSRLoading && <p>Loading...</p>}

      {isSRListError && <p>Something went wrong</p>}

      {serviceRequests?.map((sr) => (
        <div key={sr.id}>
          <Link to={`/service-request/${sr.id}`}>
            [{sr.status}] {sr.initial_complaint}
          </Link>
        </div>
      ))}

      {/* Create service request form */}
      <form onSubmit={(e) => handleCreateSR(e)}>
        <label htmlFor="vehicle-select">Vehicle:</label>
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
    </>
  );
};
