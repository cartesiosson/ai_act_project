import { Routes, Route } from "react-router-dom";
import DashboardPage from "../pages/DashboardPage";
import SystemsPage from "../pages/SystemsPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/systems" element={<SystemsPage />} />
    </Routes>
  );
}
