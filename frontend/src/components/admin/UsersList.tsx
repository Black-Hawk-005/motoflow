import { useState } from "react";

import { useUsers } from "../../hooks/admin/useUsers";
import type { User } from "../../types/auth";
import { extractErrorMessage } from "../../utils/error";

export const UsersList = () => {
  const [role, setRole] = useState<User["role"] | undefined>(undefined);
  const roleOptions: { label: string; value: User["role"] | undefined }[] = [
    { label: "All", value: undefined },
    { label: "Customer", value: "customer" },
    { label: "Mechanic", value: "mechanic" },
    { label: "Admin", value: "admin" },
  ];

  const {
    data: users,
    isLoading: isUsersLoading,
    isError: isUsersError,
    error: usersError,
  } = useUsers(role);

  return (
    <div>
      <h2 className="section-title mb-3">Users</h2>
      <div className="mb-4 flex flex-wrap gap-2">
        {roleOptions.map((r) => (
          <button
            key={r.label}
            className={role === r.value ? "btn-primary" : "btn-secondary"}
            onClick={() => setRole(r.value)}
          >
            {r.label}
          </button>
        ))}
      </div>
      {isUsersLoading && <p className="helper-text">Loading...</p>}
      <div className="overflow-x-auto">
        <table className="table-base">
          <thead>
            <tr>
              <th>S No.</th>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {users?.map((user, idx) => (
              <tr key={user.id}>
                <td>{idx + 1}</td>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td>{user.phone}</td>
                <td className="capitalize">{user.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {isUsersError && <p className="error-text">{extractErrorMessage(usersError)}</p>}
    </div>
  );
};
