import { useState, type SubmitEvent } from "react";
import { useUsers } from "../../hooks/admin/useUsers";
import { useUpdateServiceRequest } from "../../hooks/serviceRequest/useUpdateServiceRequest";
import type { ServiceStatus } from "../../types/serviceRequest";
import { extractErrorMessage } from "../../utils/error";

interface AssignMechanicControlProps {
  serviceRequestId: string;
  mechanicId: string;
  status: ServiceStatus;
}

export const AssignMechanicControl = (props: AssignMechanicControlProps) => {
  const [mechanicId, setMechanicId] = useState(props.mechanicId ?? "");

  const {
    mutate: updateServiceRequest,
    isPending: isUpdateSRPending,
    isError: isUpdateSRError,
    error: updateSRError,
  } = useUpdateServiceRequest();

  const {
    data: mechanics,
    isLoading: isMechLoading,
    isError: isMechError,
    error: mechError,
  } = useUsers("mechanic");

  const handleAssignment = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    const payload: { mechanic_id: string; status?: ServiceStatus } = {
      mechanic_id: mechanicId,
    };

    if (props.status === "pending") {
      payload.status = "assigned";
    }

    updateServiceRequest({
      id: props.serviceRequestId,
      payload,
    });
  };

  return (
    <div>
      <p className="field-label">Assign mechanic</p>
      {isMechLoading && <p className="helper-text">Loading mechanics list</p>}

      <form onSubmit={(e) => handleAssignment(e)} className="flex items-center gap-3">
        <select
          className="field-input"
          value={mechanicId}
          onChange={(e) => setMechanicId(e.target.value)}
        >
          <option value="" disabled>
            Select a mechanic
          </option>
          {mechanics?.map((mechanic) => (
            <option value={mechanic.id} key={mechanic.id}>
              {mechanic.full_name} - {mechanic.email}
            </option>
          ))}
        </select>
        <button type="submit" className="btn-primary shrink-0">
          Assign
        </button>
      </form>
      {isUpdateSRPending && <p className="helper-text">Assigning mechanic...</p>}
      {isUpdateSRError && <p className="error-text">{extractErrorMessage(updateSRError)}</p>}
      {isMechError && <p className="error-text">{extractErrorMessage(mechError)}</p>}
    </div>
  );
};
