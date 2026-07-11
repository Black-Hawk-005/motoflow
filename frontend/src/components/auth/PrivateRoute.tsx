import { Navigate, Outlet, useLocation } from "react-router-dom";

export const PrivateRoute = () => {
  const token = localStorage.getItem("token");
  const location = useLocation();

  if (token === null) {
    return <Navigate to={`/login?redirect=${location.pathname}`} replace />;
  }

  return <Outlet />;
};
