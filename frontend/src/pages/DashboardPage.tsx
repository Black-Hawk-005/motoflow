import { useEffect } from "react";
import { useMe } from "../hooks/useMe";
import { useNavigate } from "react-router-dom";

export const DashboardPage = () => {
  const { data, isLoading, isError } = useMe();
  const navigate = useNavigate();
  useEffect(() => {
    if (!data) return;
    if (data.role === "customer") navigate("/customer");
    else if (data.role === "mechanic") navigate("/mechanic");
    else navigate("/admin");
  }, [data, navigate]);
  return (
    <>
      {isLoading && <p>Loading...</p>}
      {isError && <p>Something went wrong</p>}
    </>
  );
};
