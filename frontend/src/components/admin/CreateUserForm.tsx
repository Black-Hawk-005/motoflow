import { useState } from "react";
import type { SubmitEvent } from "react";

import { useCreateUser } from "../../hooks/admin/useCreateUser";
import type { User } from "../../types/auth";

export const CreateUserForm = () => {
  const {
    mutate: createUser,
    isPending: isCreatePending,
    isError: isCreateError,
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
    <form onSubmit={(e) => handleSubmit(e)}>
      <label htmlFor="full-name-input">Full Name:</label>
      <input
        id="full-name-input"
        type="text"
        value={full_name}
        onChange={(e) => setFullName(e.target.value)}
      />

      <label htmlFor="email-input">Email:</label>
      <input
        id="email-input"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <label htmlFor="password-input">Password:</label>
      <input
        id="password-input"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <label htmlFor="phone-input">Phone:</label>
      <input
        id="phone-input"
        type="text"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />

      <label htmlFor="role-select">Role:</label>
      <select
        id="role-select"
        value={role}
        onChange={(e) => setRole(e.target.value as User["role"])}
      >
        <option value="mechanic">Mechanic</option>
        <option value="admin">Admin</option>
        <option value="customer">Customer</option>
      </select>

      <button type="submit" disabled={isCreatePending}>
        {isCreatePending ? "Creating..." : "Create User"}
      </button>

      {isCreateError && <p>Failed to create user</p>}
    </form>
  );
};
