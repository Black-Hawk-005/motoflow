import { UsersList } from "../components/admin/UsersList";
import { ServiceRequestList } from "../components/serviceRequest/ServiceRequestList";

export const AdminPage = () => {
  return (
    <>
      <h1>Admin</h1>
      <UsersList />

      <ServiceRequestList />
    </>
  );
};
