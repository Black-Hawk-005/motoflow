import { Outlet } from "react-router-dom";
import { AppHeader } from "./AppHeader";

export const Layout = () => (
  <div className="bg-slate-50">
    <AppHeader />
    <main className="mx-auto max-w-5xl space-y-6 px-6 py-6">
      <Outlet />
    </main>
  </div>
);
