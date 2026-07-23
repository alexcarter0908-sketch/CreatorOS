"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { LogOut, ChevronRight, ChevronLeft, X } from "lucide-react";

import { MAIN_NAVIGATION, SECONDARY_NAVIGATION } from "@/lib/navigation";
import { useAuthStore } from "@/features/auth/store/auth.store";
import SidebarItem from "./SidebarItem";

const APP_VERSION = "v1.0.0";
const COLLAPSE_STORAGE_KEY = "creatoros_sidebar_expanded";

function groupItems(items: typeof MAIN_NAVIGATION) {
  const groups: { label: string; items: typeof MAIN_NAVIGATION }[] = [];
  for (const item of items) {
    const existing = groups.find((g) => g.label === item.group);
    if (existing) existing.items.push(item);
    else groups.push({ label: item.group, items: [item] });
  }
  return groups;
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  return (parts[0][0] + (parts[1]?.[0] ?? "")).toUpperCase();
}

interface SidebarProps {
  /** Mobile off-canvas drawer state - ignored on desktop (md+) where the
   * sidebar is always visible. */
  open?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ open = false, onClose }: SidebarProps) {
  const pathname = usePathname();
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
  const [expanded, setExpanded] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  // Restore the last collapse/expand choice so it doesn't reset on every
  // page load. Reads after mount only, to avoid an SSR/client mismatch.
  useEffect(() => {
    const stored = window.localStorage.getItem(COLLAPSE_STORAGE_KEY);
    if (stored === "1") setExpanded(true);
    setHydrated(true);
  }, []);

  function toggleExpanded() {
    setExpanded((v) => {
      const next = !v;
      window.localStorage.setItem(COLLAPSE_STORAGE_KEY, next ? "1" : "0");
      return next;
    });
  }

  const mainGroups = groupItems(MAIN_NAVIGATION);
  const secondaryGroups = groupItems(SECONDARY_NAVIGATION);

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex h-screen shrink-0 flex-col overflow-hidden border-r border-sidebar-border bg-sidebar transition-[transform,width] duration-200 ease-out md:static md:z-auto md:translate-x-0 ${
        open ? "translate-x-0" : "-translate-x-full"
      } ${expanded ? "w-64" : "w-[72px]"} ${hydrated ? "" : "duration-0"}`}
    >
      <div className="flex items-center justify-between px-4 py-5">
        {expanded ? (
          <div className="flex min-w-0 items-center gap-2">
            <img src="/logo-icon.png" alt="Synapse-X-CreatorOS" className="h-8 w-8 shrink-0 rounded-lg object-cover" />
            <div className="min-w-0 leading-tight">
              <h1 className="truncate text-xs font-semibold text-sidebar-foreground">Synapse-X-CreatorOS</h1>
              <span className="text-[10px] text-muted-foreground">{APP_VERSION}</span>
            </div>
          </div>
        ) : (
          <img src="/logo-icon.png" alt="Synapse-X-CreatorOS" className="mx-auto h-8 w-8 rounded-lg object-cover" />
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
        onClick={toggleExpanded}
        aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
        className="mx-3 mb-4 flex shrink-0 items-center justify-center rounded-lg border border-sidebar-border py-1.5 text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
      >
        {expanded ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </button>

      <nav className="min-h-0 flex-1 space-y-1 overflow-y-auto overflow-x-hidden px-3">
        {mainGroups.map((group) => (
          <div key={group.label}>
            {expanded && (
              <p className="px-2.5 pb-1.5 pt-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground first:pt-0">
                {group.label}
              </p>
            )}
            {group.items.map((item) => (
              <SidebarItem
                key={item.href}
                href={item.href}
                label={item.title}
                icon={item.icon}
                active={pathname === item.href}
                expanded={expanded}
                flagship={item.href === "/command-center"}
              />
            ))}
          </div>
        ))}

        <div className="mt-6 space-y-1 border-t border-sidebar-border pt-6">
          {secondaryGroups.map((group) => (
            <div key={group.label}>
              {expanded && (
                <p className="px-2.5 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {group.label}
                </p>
              )}
              {group.items.map((item) => (
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
          ))}
        </div>
      </nav>

      <div className="flex shrink-0 items-center gap-2.5 border-t border-sidebar-border px-3 py-3">
        {user && (
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sidebar-accent text-[11px] font-semibold text-sidebar-accent-foreground">
            {initials(user.full_name)}
          </div>
        )}
        {expanded && user && (
          <div className="min-w-0 flex-1 leading-tight">
            <p className="truncate text-xs font-medium text-sidebar-foreground">{user.full_name}</p>
            <p className="truncate text-[10.5px] text-muted-foreground">{user.email}</p>
          </div>
        )}
        <button
          onClick={logout}
          aria-label="Logout"
          title="Logout"
          className="shrink-0 rounded-lg p-1.5 text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
        >
          <LogOut size={16} />
        </button>
      </div>
    </aside>
  );
}