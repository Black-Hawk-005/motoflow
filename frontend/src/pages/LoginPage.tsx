import { useState, type SubmitEvent } from "react";
import { useLogin } from "../hooks/auth/useLogin";
import { useNavigate, useSearchParams } from "react-router-dom";
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
    <>
      <form onSubmit={(e) => handleSubmit(e)}>
        <label htmlFor="email-input">Email:</label>
        <input
          id="email-input"
          type="email"
          onChange={(e) => setEmail(e.target.value)}
          value={email}
        ></input>
        <label htmlFor="password-input">Password:</label>
        <input
          id="password-input"
          type="password"
          onChange={(e) => setPassword(e.target.value)}
          value={password}
        ></input>
        <button type="submit" disabled={isPending}>
          {isPending ? "Logging in..." : "Login"}
        </button>
        {isError && <p>{extractErrorMessage(error)}</p>}
      </form>
    </>
  );
};
