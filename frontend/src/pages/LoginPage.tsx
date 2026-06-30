import { useState, type SubmitEvent } from "react";
import { useLogin } from "../hooks/useLogin";
import { useNavigate } from "react-router-dom";

export const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { mutate, isPending, isError } = useLogin();
  const navigate = useNavigate();

  const handleSubmit = (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    mutate(
      { email, password },
      {
        onSuccess: () => navigate("/dashboard"),
      },
    );
  };

  return (
    <>
      <form onSubmit={(e) => handleSubmit(e)}>
        <input
          type="email"
          onChange={(e) => setEmail(e.target.value)}
          value={email}
        ></input>
        <input
          type="password"
          onChange={(e) => setPassword(e.target.value)}
          value={password}
        ></input>
        <button type="submit" disabled={isPending}>
          {isPending ? "Logging in..." : "Login"}
        </button>
        {isError && <p>Login Failed</p>}
      </form>
    </>
  );
};
