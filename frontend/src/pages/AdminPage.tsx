import { UsersList } from "../components/admin/UsersList";
import { CreateUserForm } from "../components/admin/CreateUserForm";
import { AdminOverview } from "../components/admin/AdminOverview";
import { ServiceRequestList } from "../components/serviceRequest/ServiceRequestList";

export const AdminPage = () => {
  return (
    <div className="space-y-8">
      <h1 className="page-title">Admin</h1>

      <AdminOverview />

      <section className="card space-y-4">
        <h2 className="section-title">Create User</h2>
        <CreateUserForm />
      </section>

      <section className="card">
        <UsersList />
      </section>

      <section className="card">
        <ServiceRequestList />
      </section>
    </div>
  );
};
