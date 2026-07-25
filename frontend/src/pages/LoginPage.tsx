import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useState, type SubmitEvent } from "react";

import { useLogin } from "../hooks/auth/useLogin";
import { extractErrorMessage } from "../utils/error";

export const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { mutate, isPending, isError, error } = useLogin();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    mutate(
      { email, password },
      {
        onSuccess: () => navigate(searchParams.get("redirect") ?? "/dashboard"),
      },
    );
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="mb-16 w-full max-w-sm">
        <h1 className="mb-6 text-center text-2xl font-semibold text-primary">
          MotoFlow
        </h1>
        <form onSubmit={(e) => handleSubmit(e)} className="card space-y-4">
          <div>
            <label htmlFor="email-input" className="field-label">
              Email
            </label>
            <input
              id="email-input"
              type="email"
              className="field-input"
              onChange={(e) => setEmail(e.target.value)}
              value={email}
            ></input>
          </div>
          <div>
            <label htmlFor="password-input" className="field-label">
              Password
            </label>
            <input
              id="password-input"
              type="password"
              className="field-input"
              onChange={(e) => setPassword(e.target.value)}
              value={password}
            ></input>
          </div>
          <button
            type="submit"
            className="btn-primary w-full"
            disabled={isPending}
          >
            {isPending ? "Logging in..." : "Login"}
          </button>
          {isError && (
            <p className="error-text">{extractErrorMessage(error)}</p>
          )}
          <div className="text-center">
            <span className="helper-text">New here? </span>
            <Link to="/register" className="text-sm text-primary hover:underline">
              Register
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};
