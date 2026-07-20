import { useState } from "react";
import type { SubmitEvent } from "react";

import { useCreateUser } from "../../hooks/admin/useCreateUser";
import type { User } from "../../types/auth";
import { extractErrorMessage } from "../../utils/error";

export const CreateUserForm = () => {
  const {
    mutate: createUser,
    isPending: isCreatePending,
    isError: isCreateError,
    error: createUserError,
  } = useCreateUser();

  const [full_name, setFullName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [phone, setPhone] = useState<string>("");
  const [role, setRole] = useState<User["role"]>("mechanic");

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    createUser(
      { full_name, email, password, phone, role },
      {
        onSuccess: () => {
          setFullName("");
          setEmail("");
          setPassword("");
          setPhone("");
          setRole("mechanic");
        },
      },
    );
  };

  return (
    <form
      onSubmit={(e) => handleSubmit(e)}
      className="grid grid-cols-2 gap-4 sm:grid-cols-5"
    >
      <div>
        <label htmlFor="full-name-input" className="field-label">
          Full Name
        </label>
        <input
          id="full-name-input"
          type="text"
          className="field-input"
          value={full_name}
          onChange={(e) => setFullName(e.target.value)}
        />
      </div>

      <div>
        <label htmlFor="email-input" className="field-label">
          Email
        </label>
        <input
          id="email-input"
          type="email"
          className="field-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>

      <div>
        <label htmlFor="password-input" className="field-label">
          Password
        </label>
        <input
          id="password-input"
          type="password"
          className="field-input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      <div>
        <label htmlFor="phone-input" className="field-label">
          Phone
        </label>
        <input
          id="phone-input"
          type="text"
          className="field-input"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
      </div>

      <div>
        <label htmlFor="role-select" className="field-label">
          Role
        </label>
        <select
          id="role-select"
          className="field-input"
          value={role}
          onChange={(e) => setRole(e.target.value as User["role"])}
        >
          <option value="mechanic">Mechanic</option>
          <option value="admin">Admin</option>
          <option value="customer">Customer</option>
        </select>
      </div>

      <div className="col-span-2 flex items-end gap-3 sm:col-span-5">
        <button type="submit" className="btn-primary" disabled={isCreatePending}>
          {isCreatePending ? "Creating..." : "Create User"}
        </button>
        {isCreateError && (
          <p className="error-text">{extractErrorMessage(createUserError)}</p>
        )}
      </div>
    </form>
  );
};
