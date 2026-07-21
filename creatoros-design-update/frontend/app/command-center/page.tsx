"use client";

import { Suspense } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import AuthGuard from "@/components/auth/AuthGuard";
import CommandInput from "@/features/command-center/components/CommandInput";
import "@/styles/console-theme.css";

export default function CommandCenterPage() {
  return (
    <AuthGuard>
      <main className="console-theme flex h-screen flex-col overflow-hidden bg-background">
        <header className="console-glow flex shrink-0 items-center justify-between gap-3 border-b border-border px-5 py-3">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
              title="Back"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              <h1 className="font-console-display flex items-center gap-2 text-lg font-semibold text-foreground">
                Command Center
              </h1>
              <p className="font-console-mono text-[11px] text-muted-foreground">
                <span className="console-live-dot mr-1.5 align-middle" />
                CreatorOS AI &middot; Online
              </p>
            </div>
          </div>
        </header>

        <section className="min-h-0 flex-1">
          <Suspense fallback={null}>
            <CommandInput />
          </Suspense>
        </section>
      </main>
    </AuthGuard>
  );
}
