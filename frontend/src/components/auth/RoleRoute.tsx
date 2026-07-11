import { Outlet } from "react-router-dom";
import { useMe } from "../../hooks/useMe";
import type { User } from "../../types/auth";
import { Navigate } from "react-router-dom";

interface RoleRouteProps {
  allowedRoles: User["role"][];
}

export const RoleRoute = ({ allowedRoles }: RoleRouteProps) => {
  const { data, isLoading } = useMe();
  return (
    <>
      {isLoading && <p>Loading...</p>}
      {data && allowedRoles.includes(data?.role) && <Outlet />}
      {!isLoading && !data && <Navigate to="/dashboard" />}
    </>
  );
};
