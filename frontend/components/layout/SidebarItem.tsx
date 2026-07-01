import Link from "next/link";
import { LucideIcon } from "lucide-react";

interface SidebarItemProps {
  href: string;
  label: string;
  icon: LucideIcon;
  active?: boolean;
}

export default function SidebarItem({
  href,
  label,
  icon: Icon,
  active = false,
}: SidebarItemProps) {
  return (
    <Link
      href={href}
      className={`
        flex items-center gap-3
        rounded-xl
        px-4
        py-3
        transition-all
        duration-200

        ${
          active
            ? "bg-blue-600 text-white shadow-md"
            : "text-slate-300 hover:bg-slate-800 hover:text-white"
        }
      `}
    >
      <Icon size={20} />

      <span className="font-medium">
        {label}
      </span>
    </Link>
  );
}