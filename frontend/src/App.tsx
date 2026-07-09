import { Route, Routes } from "react-router-dom";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PrivateRoute } from "./components/PrivateRoute";
import { RoleRoute } from "./components/RoleRoute";
import { CustomerPage } from "./pages/CustomerPage";
import { MechanicPage } from "./pages/MechanicPage";
import { AdminPage } from "./pages/AdminPage";
import { Navigate } from "react-router-dom";
import ServiceRequestDetail from "./pages/ServiceRequestDetail";

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route element={<PrivateRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route element={<RoleRoute allowedRoles={["customer"]} />}>
            <Route path="/customer" element={<CustomerPage />} />
          </Route>
          <Route element={<RoleRoute allowedRoles={["mechanic"]} />}>
            <Route path="/mechanic" element={<MechanicPage />} />
          </Route>
          <Route element={<RoleRoute allowedRoles={["admin"]} />}>
            <Route path="/admin" element={<AdminPage />} />
          </Route>
          <Route
            path="/service-request/:id"
            element={<ServiceRequestDetail />}
          ></Route>
        </Route>
      </Routes>
    </>
  );
}

export default App;
