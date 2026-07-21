import { Link } from "react-router-dom";

import { useUsers } from "../../hooks/admin/useUsers";
import { useServiceRequests } from "../../hooks/serviceRequest/useServiceRequests";
import { StatusBadge } from "../common/StatusBadge";
import { formatDateTime } from "../../utils/date";

export const AdminOverview = () => {
  const { data: users } = useUsers();
  const { data: serviceRequests } = useServiceRequests();

  const customerCount = users?.filter((u) => u.role === "customer").length ?? 0;
  const mechanicCount = users?.filter((u) => u.role === "mechanic").length ?? 0;
  const totalRequests = serviceRequests?.length ?? 0;

  const unassigned =
    serviceRequests
      ?.filter((sr) => sr.status === "pending")
      .sort(
        (a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      ) ?? [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="card stat-tile">
          <p className="stat-tile-label">Customers</p>
          <p className="stat-tile-value">{customerCount}</p>
        </div>
        <div className="card stat-tile">
          <p className="stat-tile-label">Mechanics</p>
          <p className="stat-tile-value">{mechanicCount}</p>
        </div>
        <div className="card stat-tile">
          <p className="stat-tile-label">Service requests</p>
          <p className="stat-tile-value">{totalRequests}</p>
        </div>
        <div className="card stat-tile">
          <p className="stat-tile-label">Pending assignment</p>
          <p
            className={
              unassigned.length > 0
                ? "stat-tile-value text-orange-600"
                : "stat-tile-value"
            }
          >
            {unassigned.length}
          </p>
        </div>
      </div>

      {unassigned.length > 0 && (
        <div className="card">
          <h2 className="section-title mb-3">Needs Attention</h2>
          <ul className="divide-y divide-slate-100">
            {unassigned.map((sr) => (
              <li key={sr.id} className="py-2">
                <Link
                  to={`/service-request/${sr.id}`}
                  className="flex items-center justify-between gap-3 text-sm text-slate-700 hover:text-indigo-600"
                >
                  <span>
                    {sr.initial_complaint}
                    <span className="ml-2 text-slate-400">
                      · {formatDateTime(sr.created_at)}
                    </span>
                  </span>
                  <StatusBadge status={sr.status} />
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
