import { UsersList } from "../components/admin/UsersList";
import { CreateUserForm } from "../components/admin/CreateUserForm";
import { ServiceRequestList } from "../components/serviceRequest/ServiceRequestList";

export const AdminPage = () => {
  return (
    <>
      <h1>Admin</h1>
      <CreateUserForm />
      <UsersList />

      <ServiceRequestList />
    </>
  );
};
