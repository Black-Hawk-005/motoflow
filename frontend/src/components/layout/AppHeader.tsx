import { useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
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
    <header className="bg-primary fixed top-0 left-0 w-full shadow-md z-50">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
        <Link to={`/dashboard`}>
          <span className="text-lg font-semibold text-white transition-colors hover:text-white/80">
            MotoFlow
          </span>
        </Link>
        {user && (
          <div className="flex items-center gap-4">
            <span className="font-semibold text-white">
              {user.full_name}
              <span className="mx-2 text-white/40">|</span>
              <span className="capitalize font-semibold text-white">
                {user.role}
              </span>
            </span>
            <button
              className="rounded-md border border-white/30 bg-white/10 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-white/20"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
