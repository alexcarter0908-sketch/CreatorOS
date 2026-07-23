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

export default function SidebarItem({
  href,
  label,
  icon: Icon,
  active = false,
  expanded = true,
  flagship = false,
}: SidebarItemProps) {
  if (flagship) {
    return (
      <Link
        href={href}
        className={`group relative mb-3.5 flex items-center gap-2.5 rounded-[11px] border border-primary/35 bg-primary/10 px-3 py-2.5 text-[13.5px] font-semibold text-sidebar-foreground transition-colors hover:border-primary/60 ${
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
        {!expanded && (
          <span className="pointer-events-none absolute left-[calc(100%+10px)] top-1/2 z-20 -translate-y-1/2 whitespace-nowrap rounded-md border border-sidebar-border bg-popover px-2.5 py-1.5 text-xs font-medium text-popover-foreground opacity-0 shadow-md transition-opacity delay-100 group-hover:opacity-100">
            {label}
          </span>
        )}
      </Link>
    );
  }

  return (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={`group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
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

      {!expanded && (
        <span className="pointer-events-none absolute left-[calc(100%+10px)] top-1/2 z-20 -translate-y-1/2 whitespace-nowrap rounded-md border border-sidebar-border bg-popover px-2.5 py-1.5 text-xs font-medium text-popover-foreground opacity-0 shadow-md transition-opacity delay-100 group-hover:opacity-100">
          {label}
        </span>
      )}
    </Link>
  );
}