import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useMe } from "../../hooks/auth/useMe";

export const AppHeader = () => {
  const { data: user } = useMe();
  const navigate = useNavigate();
  const queryCient = useQueryClient();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
    queryCient.clear();
  };

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <span className="text-lg font-semibold text-indigo-600">MotoFlow</span>
        {user && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-600">
              {user.full_name}
              <span className="mx-2 text-slate-300">|</span>
              <span className="capitalize">{user.role}</span>
            </span>
            <button className="btn-secondary" onClick={handleLogout}>
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
