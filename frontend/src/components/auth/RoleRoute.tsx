import { Outlet } from "react-router-dom";
import { useMe } from "../../hooks/auth/useMe";
import type { User } from "../../types/auth";
import { Navigate } from "react-router-dom";

interface RoleRouteProps {
  allowedRoles: User["role"][];
}

export const RoleRoute = ({ allowedRoles }: RoleRouteProps) => {
  const { data, isLoading } = useMe();

  if (isLoading) {
    return <p className="helper-text">Loading...</p>;
  }

  if (!data || !allowedRoles.includes(data.role)) {
    return <Navigate to="/dashboard" />;
  }

  return <Outlet />;
};
