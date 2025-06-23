import { Routes, Route } from "react-router-dom";
import DashboardPage from "../pages/DashboardPage";
import SystemsPage from "../pages/SystemsPage";
import GraphView from "../pages/GraphView";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/systems" element={<SystemsPage />} />
      <Route path="/graph" element={<GraphView />} />
    </Routes>
  );
}
