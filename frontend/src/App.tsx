import { BrowserRouter } from "react-router-dom";
import { AppRoutes } from "./routes/AppRoutes";
import { Navbar } from "./components/Navbar";
import { MainLayout } from "./components/MainLayout";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <MainLayout>
          <AppRoutes />
        </MainLayout>
      </div>
    </BrowserRouter>
  );
}

export default App;
