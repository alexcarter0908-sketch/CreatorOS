"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { LogOut, ChevronRight, ChevronLeft, Sparkles, X } from "lucide-react";

import { MAIN_NAVIGATION, SECONDARY_NAVIGATION } from "@/lib/navigation";
import { useAuthStore } from "@/features/auth/store/auth.store";
import SidebarItem from "./SidebarItem";

const APP_VERSION = "v1.0.0";

interface SidebarProps {
  /** Mobile off-canvas drawer state - ignored on desktop (md+) where the
   * sidebar is always visible. */
  open?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ open = false, onClose }: SidebarProps) {
  const pathname = usePathname();
  const logout = useAuthStore((state) => state.logout);
  const [expanded, setExpanded] = useState(false);

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex h-screen shrink-0 flex-col border-r border-sidebar-border bg-sidebar transition-transform duration-200 md:static md:z-auto md:translate-x-0 ${
        open ? "translate-x-0" : "-translate-x-full"
      } ${expanded ? "w-64" : "w-[72px]"}`}
    >
      <div className="flex items-center justify-between px-4 py-5">
        {expanded ? (
          <div className="flex min-w-0 items-center gap-2">
            <img src="/logo.png" alt="Synapse-X-CreatorOS" className="h-8 w-8 shrink-0 rounded-lg object-cover" />
            <div className="min-w-0 leading-tight">
              <h1 className="truncate text-xs font-semibold text-sidebar-foreground">Synapse-X-CreatorOS</h1>
              <span className="text-[10px] text-muted-foreground">{APP_VERSION}</span>
            </div>
          </div>
        ) : (
          <img src="/logo.png" alt="Synapse-X-CreatorOS" className="mx-auto h-8 w-8 rounded-lg object-cover" />
        )}
        <button
          onClick={onClose}
          aria-label="Close menu"
          className="text-muted-foreground hover:text-sidebar-foreground md:hidden"
        >
          <X size={18} />
        </button>
      </div>

      <button
        onClick={() => setExpanded((v) => !v)}
        className="mx-3 mb-4 flex shrink-0 items-center justify-center rounded-lg border border-sidebar-border py-1.5 text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
      >
        {expanded ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </button>

      <nav className="min-h-0 flex-1 space-y-1 overflow-y-auto px-3">
        {MAIN_NAVIGATION.map((item) => (
          <SidebarItem
            key={item.href}
            href={item.href}
            label={item.title}
            icon={item.icon}
            active={pathname === item.href}
            expanded={expanded}
          />
        ))}

        <div className="mt-6 space-y-1 border-t border-sidebar-border pt-6">
          {SECONDARY_NAVIGATION.map((item) => (
            <SidebarItem
              key={item.href}
              href={item.href}
              label={item.title}
              icon={item.icon}
              active={pathname === item.href}
              expanded={expanded}
            />
          ))}
        </div>
      </nav>

      <button
        onClick={logout}
        className="mx-3 mb-4 flex shrink-0 items-center gap-3 rounded-lg px-3 py-2.5 text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
        title="Logout"
      >
        <LogOut size={18} className="shrink-0" />
        {expanded && <span className="text-sm font-medium">Logout</span>}
      </button>
    </aside>
  );
}