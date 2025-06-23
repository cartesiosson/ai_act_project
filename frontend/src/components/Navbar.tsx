import { Link } from "react-router-dom";

export function Navbar() {
  return (
    <nav className="bg-white shadow-md dark:bg-gray-800 p-4 flex gap-6">
      <Link to="/" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Dashboard</Link>
      <Link to="/systems" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Systems</Link>
      <Link to="/graph" className="font-semibold text-blue-600 dark:text-blue-400 hover:underline">Graph View</Link>
    </nav>
  );
}
