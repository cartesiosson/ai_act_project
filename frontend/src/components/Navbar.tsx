import { Link } from "react-router-dom";

export function Navbar() {
  return (
    <nav className="bg-white shadow-md dark:bg-gray-800 px-4 py-3 flex items-center justify-between">
      {/* Logos UNIR + SERAMIS */}
      <div className="flex items-center gap-4">
        <img
          src="/logo-unir.png"
          alt="UNIR - Universidad Internacional de La Rioja"
          className="h-10 object-contain"
        />
        <img
          src="/seramis-logo.svg"
          alt="SERAMIS - Semantic Regulation Intelligence System"
          className="h-10 object-contain"
        />
        <span className="text-gray-400 dark:text-gray-500">|</span>
        <span className="text-base font-bold text-gray-700 dark:text-gray-200">
          Semantic Regulation Intelligence System
        </span>
      </div>

      {/* Navigation Links */}
      <div className="flex gap-6">
        <Link to="/" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Dashboard</Link>
        <Link to="/systems" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">AI Systems DB</Link>
        <Link to="/graph" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">AI Knowledge Graph</Link>
        <Link to="/ontology" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Ontology Docs</Link>
        <Link to="/reasoning" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">AI Symbolic Reasoning</Link>
        <Link to="/forensic" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Forensic AI Agent</Link>
      </div>
    </nav>
  );
}
