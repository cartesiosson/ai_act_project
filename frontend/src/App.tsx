import { BrowserRouter } from "react-router-dom";
import { AppRoutes } from "./routes/AppRoutes";
import { Navbar } from "./components/Navbar";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow p-4 bg-gray-100 dark:bg-gray-900">
          <AppRoutes />
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
