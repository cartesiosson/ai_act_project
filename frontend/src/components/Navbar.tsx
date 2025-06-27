import { Link } from "react-router-dom";

export function Navbar() {
  const locale = navigator.language.startsWith("es") ? "es" : "en";
  const docsUrl = `http://localhost/docs/index-${locale}.html`;

  return (
    <nav className="bg-white shadow-md dark:bg-gray-800 p-4 flex gap-6">
      <Link to="/" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Dashboard</Link>
      <Link to="/systems" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Systems</Link>
      <Link to="/graph" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Graph View</Link>
      <Link to="/ontology" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Ontology Docs</Link>
      <Link to="/reasoning" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Reasoning</Link>
    </nav>
  );
}
