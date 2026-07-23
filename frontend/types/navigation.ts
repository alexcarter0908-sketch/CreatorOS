import type { LucideIcon } from "lucide-react";

export interface NavigationItem {
  title: string;
  href: string;
  icon: LucideIcon;
  /** Section label shown above this item in the sidebar. */
  group: string;
}