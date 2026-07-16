import { useState, type SubmitEvent } from "react";
import { useUsers } from "../../hooks/admin/useUsers";
import { useUpdateServiceRequest } from "../../hooks/serviceRequest/useUpdateServiceRequest";

interface AssignMechanicControlProps {
  serviceRequestId: string;
}

export const AssignMechanicControl = (props: AssignMechanicControlProps) => {
  const [mechanicId, setMechanicId] = useState("");

  const {
    mutate: updateServiceRequest,
    isPending: isUpdateSRPending,
    isError: isUpdateSRError,
  } = useUpdateServiceRequest();

  const {
    data: mechanics,
    isLoading: isMechLoading,
    isError: isMechError,
  } = useUsers("mechanic");

  const handleAssignment = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    updateServiceRequest({
      id: props.serviceRequestId,
      payload: {
        mechanic_id: mechanicId,
        status: "assigned",
      },
    });
  };

  return (
    <div>
      <p>Assign mechanic</p>
      {isMechLoading && <p>Loading mechanics list</p>}

      <form onSubmit={(e) => handleAssignment(e)}>
        <select
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
        <button type="submit">Assign</button>
      </form>
      {isUpdateSRPending && <p>Assigning mechanic...</p>}
      {isUpdateSRError && <p>Unable to assign mechanic</p>}
      {isMechError && <p>Unable to load mechanics list</p>}
    </div>
  );
};
