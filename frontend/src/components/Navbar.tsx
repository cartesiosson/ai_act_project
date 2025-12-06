import { Link } from "react-router-dom";

export function Navbar() {
  return (
    <nav className="bg-white shadow-md dark:bg-gray-800 px-4 py-3 flex items-center justify-between">
      {/* Logo UNIR */}
      <div className="flex items-center gap-4">
        <img
          src="/logo-unir.png"
          alt="UNIR - Universidad Internacional de La Rioja"
          className="h-10 object-contain"
        />
        <span className="text-gray-400 dark:text-gray-500">|</span>
        <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
          TFM - AI Act Compliance
        </span>
      </div>

      {/* Navigation Links */}
      <div className="flex gap-6">
        <Link to="/" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Dashboard</Link>
        <Link to="/systems" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Systems</Link>
        <Link to="/graph" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Graph View</Link>
        <Link to="/ontology" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Ontology Docs</Link>
        <Link to="/reasoning" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Reasoning</Link>
      </div>
    </nav>
  );
}
