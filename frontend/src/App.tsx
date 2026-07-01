import { Route, Routes } from "react-router-dom";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import "./App.css";
import { PrivateRoute } from "./components/PrivateRoute";
import { CustomerPage } from "./pages/CustomerPage";
import { MechanicPage } from "./pages/MechanicPage";
import { AdminPage } from "./pages/AdminPage";
import { Navigate } from "react-router-dom";

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route element={<PrivateRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/customer" element={<CustomerPage />} />
          <Route path="/mechanic" element={<MechanicPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
