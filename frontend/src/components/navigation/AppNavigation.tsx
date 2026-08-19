import {
  NavLink,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import {
  getRoleLabel,
  canAccessAnalytics,
  canManageUsers,
} from "../../utils/roles";

import NotificationCenter from "../notifications/NotificationCenter";

function navClass({
  isActive,
}: {
  isActive: boolean;
}) {
  return [
    "app-nav-link",
    isActive ? "app-nav-link-active" : "",
  ]
    .filter(Boolean)
    .join(" ");
}

export default function AppNavigation() {
  const {
    user,
    logout,
  } = useAuth();

  const navigate = useNavigate();

  if (!user) {
    return null;
  }

  return (
    <header className="app-navigation">
      <div className="app-navigation-brand">
        <button
          type="button"
          className="app-brand-button"
          onClick={() =>
            navigate("/dashboard")
          }
        >
          <span className="app-brand-mark">
            R
          </span>

          <span className="app-brand-text">
            <strong>ResQAI</strong>
            <small>
              Emergency Intelligence
            </small>
          </span>
        </button>
      </div>

      <nav className="app-navigation-links">
        <NavLink
          to="/dashboard"
          className={navClass}
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/incidents"
          className={navClass}
        >
          Incidents
        </NavLink>

        <NavLink
          to="/incidents/new"
          className={navClass}
        >
          Report Incident
        </NavLink>

        {canAccessAnalytics(
          user.role
        ) && (
          <NavLink
            to="/analytics"
            className={navClass}
          >
            Analytics
          </NavLink>
        )}

        {canManageUsers(
          user.role
        ) && (
          <NavLink
            to="/users"
            className={navClass}
          >
            Users
          </NavLink>
        )}
      </nav>

      <div className="app-navigation-actions">
        <NotificationCenter compact />

        <div className="app-user">
          <strong>
            {user.full_name}
          </strong>

          <span>
            {getRoleLabel(user.role)}
          </span>
        </div>

        <button
          type="button"
          className="app-logout"
          onClick={logout}
        >
          Logout
        </button>
      </div>
    </header>
  );
}