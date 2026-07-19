import { useState, type SubmitEvent, useEffect } from "react";

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
      <h2>Users</h2>
      {isUsersLoading && <p>Loading...</p>}
      {roleOptions.map((r) => (
        <button onClick={() => setRole(r.value)}>{r.label}</button>
      ))}
      <table>
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
            <tr>
              <td>{idx + 1}</td>
              <td>{user.full_name}</td>
              <td>{user.email}</td>
              <td>{user.phone}</td>
              <td>{user.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {isUsersError && <p>{extractErrorMessage(usersError)}</p>}
    </div>
  );
};
