import {
  LayoutDashboard,
  FolderKanban,
  Terminal,
  Zap,
  FileText,
  Image,
  Video,
  Search,
  BarChart3,
  CreditCard,
  Settings,
  HelpCircle,
  Youtube,
  FileBarChart,
} from "lucide-react";

import type { NavigationItem } from "@/types/navigation";

export const MAIN_NAVIGATION: NavigationItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Connections", href: "/connections", icon: Youtube },
  { title: "Projects", href: "/projects", icon: FolderKanban },
  { title: "Command Center", href: "/command-center", icon: Terminal },
  { title: "Automation", href: "/automation", icon: Zap },
  { title: "Scripts", href: "/scripts", icon: FileText },
  { title: "Thumbnails", href: "/thumbnails", icon: Image },
  { title: "Videos", href: "/videos", icon: Video },
  { title: "SEO", href: "/seo", icon: Search },
];

export const SECONDARY_NAVIGATION: NavigationItem[] = [
  { title: "Analytics", href: "/analytics", icon: BarChart3 },
  { title: "Reports", href: "/reports", icon: FileBarChart },
  { title: "Billing", href: "/billing", icon: CreditCard },
  { title: "Settings", href: "/settings", icon: Settings },
  { title: "Help", href: "/help", icon: HelpCircle },
];