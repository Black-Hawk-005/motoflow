import { useState } from "react";
import { Link } from "react-router-dom";
import type { SubmitEvent } from "react";

import { extractErrorMessage } from "../../utils/error";
import { useRegister } from "../../hooks/auth/useRegister";

export const RegisterUserForm = () => {
  const {
    mutate: register,
    isPending: isRegisterPending,
    isError: isRegisterError,
    isSuccess: isRegisterSuccess,
    error: registerError,
  } = useRegister();

  const [full_name, setFullName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [phone, setPhone] = useState<string>("");

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    register(
      { full_name, email, password, phone },
      {
        onSuccess: () => {
          setFullName("");
          setEmail("");
          setPassword("");
          setPhone("");
        },
      },
    );
  };

  if (isRegisterSuccess) {
    return (
      <div className="space-y-4 text-center">
        <p className="info-value">
          Registration submitted. An admin needs to approve your account
          before you can log in.
        </p>
        <Link to="/login" className="btn-primary inline-flex">
          Back to Login
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={(e) => handleSubmit(e)} className="space-y-4">
      <p className="helper-text">
        New accounts require admin approval before you can log in.
      </p>

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

      <button
        type="submit"
        className="btn-primary w-full"
        disabled={isRegisterPending}
      >
        {isRegisterPending ? "Registering..." : "Register"}
      </button>

      {isRegisterError && (
        <p className="error-text">{extractErrorMessage(registerError)}</p>
      )}

      <div className="text-center">
        <Link to="/login" className="text-sm text-primary hover:underline">
          Back to Login
        </Link>
      </div>
    </form>
  );
};
