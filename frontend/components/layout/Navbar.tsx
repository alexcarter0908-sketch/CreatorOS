"use client";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useAuthStore } from "@/features/auth/store/auth.store";
import ThemeToggle from "@/components/theme/ThemeToggle";
export default function Navbar() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const initial = user?.full_name?.charAt(0)?.toUpperCase() ?? "?";
  return (
    <header className="flex items-center justify-between border-b border-border bg-background/80 px-8 py-5 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          title="Back"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">Dashboard</h2>
          <p className="text-base text-muted-foreground">Welcome back to CreatorOS</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        <span className="text-base font-medium text-foreground">
          {user?.full_name ?? "..."}
        </span>
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
          {initial}
        </div>
      </div>
    </header>
  );
}