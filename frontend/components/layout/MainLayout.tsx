import { ReactNode } from "react";
import AuthGuard from "@/components/auth/AuthGuard";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <AuthGuard>
      <main className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Navbar />
          <section className="flex-1 overflow-y-auto p-8">{children}</section>
        </div>
      </main>
    </AuthGuard>
  );
}