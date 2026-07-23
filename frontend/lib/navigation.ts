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
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard, group: "Overview" },
  { title: "Command Center", href: "/command-center", icon: Terminal, group: "Create" },
  { title: "Projects", href: "/projects", icon: FolderKanban, group: "Create" },
  { title: "Scripts", href: "/scripts", icon: FileText, group: "Create" },
  { title: "Thumbnails", href: "/thumbnails", icon: Image, group: "Create" },
  { title: "Videos", href: "/videos", icon: Video, group: "Create" },
  { title: "SEO", href: "/seo", icon: Search, group: "Grow" },
  { title: "Automation", href: "/automation", icon: Zap, group: "Grow" },
  { title: "Connections", href: "/connections", icon: Youtube, group: "Grow" },
];

export const SECONDARY_NAVIGATION: NavigationItem[] = [
  { title: "Analytics", href: "/analytics", icon: BarChart3, group: "Workspace" },
  { title: "Reports", href: "/reports", icon: FileBarChart, group: "Workspace" },
  { title: "Billing", href: "/billing", icon: CreditCard, group: "Workspace" },
  { title: "Settings", href: "/settings", icon: Settings, group: "Workspace" },
  { title: "Help", href: "/help", icon: HelpCircle, group: "Workspace" },
];