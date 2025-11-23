import { useLocation, ReactNode } from "react-router-dom";

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const location = useLocation();
  const isGraphView = location.pathname === "/graph";

  return (
    <main className={`flex-grow ${isGraphView ? "" : "p-4"} ${isGraphView ? "bg-gray-900" : "bg-gray-100 dark:bg-gray-900"}`}>
      {children}
    </main>
  );
}
