import Link from "next/link";
import { LucideIcon } from "lucide-react";

interface SidebarItemProps {
  href: string;
  label: string;
  icon: LucideIcon;
  active?: boolean;
  expanded?: boolean;
}

export default function SidebarItem({
  href,
  label,
  icon: Icon,
  active = false,
  expanded = true,
}: SidebarItemProps) {
  return (
    <Link
      href={href}
      title={label}
      className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
        active
          ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
          : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
      } ${expanded ? "" : "justify-center"}`}
    >
      <Icon size={18} className="shrink-0" />
      {expanded && <span className="truncate">{label}</span>}
    </Link>
  );
}