import { Link } from "react-router-dom";

import { UsersList } from "../components/admin/UsersList";
import { AdminOverview } from "../components/admin/AdminOverview";
import { ServiceRequestList } from "../components/serviceRequest/ServiceRequestList";

export const AdminPage = () => {
  return (
    <div className="space-y-5">
      <h1 className="page-title">Admin</h1>

      <AdminOverview />

      <section className="card">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="section-title">Users</h2>
          <Link to="/admin/create-user" className="btn-primary">
            Create User
          </Link>
        </div>
        <UsersList />
      </section>

      <section className="card">
        <ServiceRequestList />
      </section>
    </div>
  );
};
