import { useState } from "react";

import { useUsers } from "../../hooks/admin/useUsers";
import type { User } from "../../types/auth";
import { extractErrorMessage } from "../../utils/error";
import { useApproveUser } from "../../hooks/admin/useApproveUser";

export const UsersList = () => {
  const [role, setRole] = useState<User["role"] | undefined>(undefined);
  const [approvalState, setApprovalState] = useState<boolean | undefined>(
    undefined,
  );

  const roleOptions: { label: string; value: User["role"] | undefined }[] = [
    { label: "All", value: undefined },
    { label: "Customer", value: "customer" },
    { label: "Mechanic", value: "mechanic" },
    { label: "Admin", value: "admin" },
  ];

  const approvalStateOptions: { label: string; value: boolean | undefined }[] =
    [
      { label: "All", value: undefined },
      { label: "Approved", value: true },
      { label: "Approval Pending", value: false },
    ];

  const {
    data: users,
    isLoading: isUsersLoading,
    isError: isUsersError,
    error: usersError,
  } = useUsers(role, approvalState);

  const [approvingId, setApprovingId] = useState<string | null>(null);

  const {
    mutate: approveUser,
    isPending: isApprovePending,
    isError: isApproveError,
    error: approveError,
  } = useApproveUser();

  const handleApprove = (userId: string) => {
    setApprovingId(userId);
    approveUser(userId, { onSettled: () => setApprovingId(null) });
  };

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <span className="ml-2 text-sm text-slate-700">Role:</span>
        {roleOptions.map((r) => (
          <button
            key={r.label}
            className={role === r.value ? "btn-primary" : "btn-secondary"}
            onClick={() => setRole(r.value)}
          >
            {r.label}
          </button>
        ))}
        <span className="ml-3 text-sm text-slate-700">Approval:</span>
        {approvalStateOptions.map((as) => (
          <button
            key={as.label}
            className={
              approvalState === as.value ? "btn-primary" : "btn-secondary"
            }
            onClick={() => setApprovalState(as.value)}
          >
            {as.label}
          </button>
        ))}
      </div>

      {isUsersLoading && <p className="helper-text">Loading...</p>}

      {isUsersError && (
        <p className="error-text">{extractErrorMessage(usersError)}</p>
      )}

      {!isUsersLoading && users?.length === 0 && (
        <p className="helper-text">No users match these filters.</p>
      )}

      {!isUsersLoading && users && users.length > 0 && (
        <div className="overflow-x-auto">
          <table className="table-base">
            <thead>
              <tr>
                <th>S No.</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Approval State</th>
                <th>Approve</th>
              </tr>
            </thead>
            <tbody>
              {[...users]
                .sort((a, b) => Number(a.is_approved) - Number(b.is_approved))
                .map((user, idx) => (
                  <tr key={user.id}>
                    <td>{idx + 1}</td>
                    <td>{user.full_name}</td>
                    <td>{user.email}</td>
                    <td>{user.phone}</td>
                    <td className="capitalize">{user.role}</td>
                    <td>
                      <span
                        className={
                          user.is_approved
                            ? "badge-approved"
                            : "badge-action_required"
                        }
                      >
                        {user.is_approved ? "Approved" : "Needs Approval"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-primary"
                        onClick={() => handleApprove(user.id)}
                        disabled={
                          user.is_approved ||
                          (isApprovePending && approvingId === user.id)
                        }
                      >
                        {isApprovePending && approvingId === user.id
                          ? "Approving"
                          : "Approve"}
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {isApproveError && (
            <p className="error-text mt-2">
              {extractErrorMessage(approveError)}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
