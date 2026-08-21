import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../context/useAuth";
import type { UserRole } from "../api/auth";

interface RoleGuardProps {
  allowedRoles: UserRole[];
}

export default function RoleGuard({
  allowedRoles,
}: RoleGuardProps) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        Loading...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }

  return <Outlet />;
}