import { Routes, Route } from "react-router-dom";
import DashboardPage from "../pages/DashboardPage";
import SystemsPage from "../pages/SystemsPage";
import GraphView from "../pages/GraphView";
import OntologyDocs from "../pages/OntologyDocs";
import ReasoningPage from "../pages/ReasoningPage";
import ForensicAgentPage from "../pages/ForensicAgentPage";
import DPVPage from "../pages/DPVPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/systems" element={<SystemsPage />} />
      <Route path="/graph" element={<GraphView />} />
      <Route path="/ontology" element={<OntologyDocs />} />
      <Route path="/reasoning" element={<ReasoningPage />} />
      <Route path="/forensic" element={<ForensicAgentPage />} />
      <Route path="/dpv" element={<DPVPage />} />
    </Routes>
  );
}
