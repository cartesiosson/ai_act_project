import { Routes, Route } from "react-router-dom";
import DashboardPage from "../pages/DashboardPage";
import SystemsPage from "../pages/SystemsPage";
import GraphView from "../pages/GraphView";
import OntologyDocs from "../pages/OntologyDocs";
import ReasoningPage from "../pages/ReasoningPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/systems" element={<SystemsPage />} />
      <Route path="/graph" element={<GraphView />} />
      <Route path="/ontology" element={<OntologyDocs />} />
      <Route path="/reasoning" element={<ReasoningPage />} />
    </Routes>
  );
}
