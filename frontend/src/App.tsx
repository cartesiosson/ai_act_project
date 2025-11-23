import { BrowserRouter, useLocation } from "react-router-dom";
import { AppRoutes } from "./routes/AppRoutes";
import { Navbar } from "./components/Navbar";

function App() {
  const location = useLocation();
  const isGraphView = location.pathname === "/graph";

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className={`flex-grow ${isGraphView ? "" : "p-4"} ${isGraphView ? "bg-gray-900" : "bg-gray-100 dark:bg-gray-900"}`}>
          <AppRoutes />
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
