import { Outlet } from "react-router-dom";

import AppNavigation from "./AppNavigation";

export default function AppShell() {
  return (
    <div className="app-shell">
      <AppNavigation />

      <main className="app-shell-content">
        <Outlet />
      </main>
    </div>
  );
}