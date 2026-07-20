"use client";

import { Suspense } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import AuthGuard from "@/components/auth/AuthGuard";
import CommandInput from "@/features/command-center/components/CommandInput";

export default function CommandCenterPage() {
  return (
    <AuthGuard>
      <main className="flex h-screen flex-col overflow-hidden bg-background">
        <header className="flex shrink-0 items-center gap-3 border-b border-border px-4 py-3">
          <Link
            href="/dashboard"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
            title="Back"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="flex items-baseline gap-1.5 font-semibold text-foreground"><span className="text-base">Welcome to</span><span className="text-2xl">CreatorOS</span></h1>
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
