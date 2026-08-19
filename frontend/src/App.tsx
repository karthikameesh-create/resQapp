import {
  lazy,
  Suspense,
} from "react";
import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import RoleGuard from "./components/RoleGuard";
import AppShell from "./components/navigation/AppShell";
import LoadingState from "./components/ui/LoadingState";

import { useAuth } from "./context/AuthContext";

const Analytics = lazy(
  () => import("./pages/Analytics")
);

const CreateIncident = lazy(
  () => import("./pages/CreateIncident")
);

const Dashboard = lazy(
  () => import("./pages/Dashboard")
);

const IncidentDetails = lazy(
  () => import("./pages/IncidentDetails")
);

const Incidents = lazy(
  () => import("./pages/Incidents")
);

const Login = lazy(
  () => import("./pages/Login")
);

const Register = lazy(
  () => import("./pages/Register")
);

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Suspense
      fallback={
        <LoadingState message="Loading ResQAI..." />
      }
    >
      <Routes>
        <Route
          path="/"
          element={
            <Navigate
              to={
                isAuthenticated
                  ? "/dashboard"
                  : "/login"
              }
              replace
            />
          }
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/incidents"
              element={<Incidents />}
            />

            <Route
              path="/incidents/new"
              element={<CreateIncident />}
            />

            <Route
              path="/incidents/:incidentId"
              element={<IncidentDetails />}
            />

            <Route
              element={
                <RoleGuard
                  allowedRoles={[
                    "responder",
                    "admin",
                  ]}
                />
              }
            >
              <Route
                path="/analytics"
                element={<Analytics />}
              />
            </Route>

            <Route
              element={
                <RoleGuard
                  allowedRoles={["admin"]}
                />
              }
            >
              <Route
                path="/users"
                element={
                  <div className="role-placeholder">
                    <h1>
                      User Management
                    </h1>

                    <p>
                      Administrator user
                      management will be
                      added here.
                    </p>
                  </div>
                }
              />
            </Route>
          </Route>
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;