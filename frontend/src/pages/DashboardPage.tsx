import { useEffect } from "react";
import { useMe } from "../hooks/auth/useMe";
import { useNavigate } from "react-router-dom";

export const DashboardPage = () => {
  const { data, isLoading, isError } = useMe();
  const navigate = useNavigate();
  useEffect(() => {
    if (!data) return;
    if (data.role === "customer") navigate("/customer");
    else if (data.role === "mechanic") navigate("/mechanic");
    else if (data.role === "admin") navigate("/admin");
    else navigate("/login");
  }, [data]);
  return (
    <>
      {isLoading && <p className="helper-text">Loading...</p>}
      {isError && <p className="error-text">Something went wrong</p>}
    </>
  );
};
