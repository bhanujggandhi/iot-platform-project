import { useLocation, Navigate, Outlet } from "react-router-dom";
import useAuth from "../hooks/useAuth";

const RequireAuth = ({ allowedRoles }) => {
  const { auth } = useAuth();
  const location = useLocation();
  const token = localStorage.getItem("token");
  const hasRequiredRole = auth?.roles?.find((role) =>
    allowedRoles?.includes(role)
  );

  return token ? (
    hasRequiredRole ? (
      <Outlet />
    ) : (
      <Navigate to="/unauthorized" state={{ from: location }} replace />
    )
  ) : auth?.user ? (
    <Navigate to="/unauthorized" state={{ from: location }} replace />
  ) : (
    <Navigate to="/devLogin" state={{ from: location }} replace />
  );
};

export default RequireAuth;
