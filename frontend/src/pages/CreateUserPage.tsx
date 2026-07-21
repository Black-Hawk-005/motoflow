import { Link } from "react-router-dom";

import { CreateUserForm } from "../components/admin/CreateUserForm";

export const CreateUserPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Create User</h1>
        <Link to="/admin" className="btn-secondary">
          Back to Dashboard
        </Link>
      </div>

      <div className="card">
        <CreateUserForm />
      </div>
    </div>
  );
};
