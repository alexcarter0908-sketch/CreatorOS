"use client";

import { useRef, useState } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { LucideIcon } from "lucide-react";

interface SidebarItemProps {
  href: string;
  label: string;
  icon: LucideIcon;
  active?: boolean;
  expanded?: boolean;
  /** Special highlighted treatment for Command Center - the app's
   * flagship AI entry point, visually separated from regular items. */
  flagship?: boolean;
}

/** Renders `label` in a small floating box positioned next to whatever
 * element is currently hovered, via a portal straight to <body> so it
 * can never be clipped by the sidebar's own scroll container. */
function useHoverTooltip(label: string, disabled: boolean) {
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null);
  const ref = useRef<HTMLAnchorElement>(null);

  const handlers = disabled
    ? {}
    : {
        onMouseEnter: () => {
          const rect = ref.current?.getBoundingClientRect();
          if (rect) setPos({ top: rect.top + rect.height / 2, left: rect.right + 10 });
        },
        onMouseLeave: () => setPos(null),
      };

  const portal =
    pos && typeof document !== "undefined"
      ? createPortal(
          <span
            className="pointer-events-none fixed z-[100] -translate-y-1/2 whitespace-nowrap rounded-md border border-sidebar-border bg-popover px-2.5 py-1.5 text-xs font-medium text-popover-foreground shadow-md"
            style={{ top: pos.top, left: pos.left }}
          >
            {label}
          </span>,
          document.body
        )
      : null;

  return { ref, handlers, portal };
}

export default function SidebarItem({
  href,
  label,
  icon: Icon,
  active = false,
  expanded = true,
  flagship = false,
}: SidebarItemProps) {
  const { ref, handlers, portal } = useHoverTooltip(label, expanded);

  if (flagship) {
    return (
      <>
        <Link
          ref={ref}
          href={href}
          {...handlers}
          className={`relative mb-3.5 flex items-center gap-2.5 rounded-[11px] border border-primary/35 bg-primary/10 px-3 py-2.5 text-[13.5px] font-semibold text-sidebar-foreground transition-colors hover:border-primary/60 ${
            expanded ? "" : "justify-center px-0"
          }`}
        >
          <Icon size={18} className="shrink-0 text-primary" />
          {expanded && <span className="truncate">{label}</span>}
          <span
            className={`h-[7px] w-[7px] shrink-0 rounded-full bg-emerald-400 shadow-[0_0_0_4px_rgba(52,211,153,0.18)] ${
              expanded ? "ml-auto" : "absolute right-1.5 top-1.5"
            }`}
          />
        </Link>
        {portal}
      </>
    );
  }

  return (
    <>
      <Link
        ref={ref}
        href={href}
        {...handlers}
        aria-current={active ? "page" : undefined}
        className={`relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
          active
            ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
            : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
        } ${expanded ? "" : "justify-center"}`}
      >
        {active && (
          <span className="absolute -left-3 top-1.5 bottom-1.5 w-[3px] rounded-full bg-primary" />
        )}
        <Icon size={18} className={`shrink-0 ${active ? "text-primary" : ""}`} />
        {expanded && <span className="truncate">{label}</span>}
      </Link>
      {portal}
    </>
  );
}