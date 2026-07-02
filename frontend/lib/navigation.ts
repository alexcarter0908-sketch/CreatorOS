import {
  LayoutDashboard,
  FolderKanban,
  FileText,
  Image,
  Video,
  Search,
  BarChart3,
  CreditCard,
  Settings,
  HelpCircle,
} from "lucide-react";

import { NavigationItem } from "../types/navigation";

export const MAIN_NAVIGATION: NavigationItem[] = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Projects",
    href: "/projects",
    icon: FolderKanban,
  },
  {
    title: "Scripts",
    href: "/scripts",
    icon: FileText,
  },
  {
    title: "Thumbnails",
    href: "/thumbnails",
    icon: Image,
  },
  {
    title: "Videos",
    href: "/videos",
    icon: Video,
  },
  {
    title: "SEO",
    href: "/seo",
    icon: Search,
  },
];

export const SECONDARY_NAVIGATION: NavigationItem[] = [
  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    title: "Billing",
    href: "/billing",
    icon: CreditCard,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
  {
    title: "Help",
    href: "/help",
    icon: HelpCircle,
  },
];