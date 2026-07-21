"use client";
import { useRouter, usePathname } from "next/navigation";
import { ArrowLeft, Menu } from "lucide-react";
import { useAuthStore } from "@/features/auth/store/auth.store";
import ThemeToggle from "@/components/theme/ThemeToggle";
import { MAIN_NAVIGATION, SECONDARY_NAVIGATION } from "@/lib/navigation";

interface NavbarProps {
  onMenuClick?: () => void;
}

function usePageTitle(pathname: string): string {
  const all = [...MAIN_NAVIGATION, ...SECONDARY_NAVIGATION];
  const match = all.find(
    (item) => pathname === item.href || pathname.startsWith(`${item.href}/`)
  );
  return match?.title ?? "CreatorOS";
}

export default function Navbar({ onMenuClick }: NavbarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);
  const initial = user?.full_name?.charAt(0)?.toUpperCase() ?? "?";
  const pageTitle = usePageTitle(pathname);

  return (
    <header className="flex items-center justify-between border-b border-border bg-background/80 px-4 py-5 backdrop-blur-sm sm:px-8">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          title="Menu"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground md:hidden"
        >
          <Menu className="h-4 w-4" />
        </button>
        <button
          onClick={() => router.back()}
          title="Back"
          className="hidden h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground sm:flex"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-foreground sm:text-2xl">
            {pageTitle}
          </h2>
          <p className="hidden text-base text-muted-foreground sm:block">
            Welcome back to CreatorOS
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />
        <span className="hidden text-base font-medium text-foreground sm:inline">
          {user?.full_name ?? "..."}
        </span>
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground sm:h-10 sm:w-10">
          {initial}
        </div>
      </div>
    </header>
  );
}
