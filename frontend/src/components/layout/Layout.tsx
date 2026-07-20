import { Outlet } from "react-router-dom";
import { AppHeader } from "./AppHeader";

export const Layout = () => (
  <div className="min-h-screen bg-slate-50">
    <AppHeader />
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-8">
      <Outlet />
    </main>
  </div>
);
