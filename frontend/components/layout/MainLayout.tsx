"use client";

import { ReactNode, useState } from "react";
import AuthGuard from "@/components/auth/AuthGuard";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <AuthGuard>
      <main className="flex h-screen overflow-hidden bg-background">
        <Sidebar open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />

        {mobileNavOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 md:hidden"
            onClick={() => setMobileNavOpen(false)}
            aria-hidden="true"
          />
        )}

        <div className="flex flex-1 flex-col overflow-hidden">
          <Navbar onMenuClick={() => setMobileNavOpen(true)} />
          <section className="flex-1 overflow-y-auto p-8">{children}</section>
        </div>
      </main>
    </AuthGuard>
  );
}
