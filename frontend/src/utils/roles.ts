import type { UserRole } from "../api/auth";

export const roleLabels: Record<UserRole, string> = {
  citizen: "Citizen",
  responder: "Responder",
  admin: "Administrator",
};

export function getRoleLabel(
  role: UserRole
): string {
  return roleLabels[role] ?? role;
}

export function canAccessAnalytics(
  role: UserRole
): boolean {
  return (
    role === "responder" ||
    role === "admin"
  );
}

export function canManageUsers(
  role: UserRole
): boolean {
  return role === "admin";
}

export function canManageIncidents(
  role: UserRole
): boolean {
  return (
    role === "responder" ||
    role === "admin"
  );
}