"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import MainLayout from "@/components/layout/MainLayout";
import StatsCard from "@/components/dashboard/StatsCard";
import QuickActions from "@/components/dashboard/QuickActions";
import RecentProjects from "@/components/dashboard/RecentProjects";

import { useDashboardStats } from "@/lib/hooks/useDashboardStats";

import {
  FolderKanban,
  FileText,
  Video,
  Coins,
  ImageIcon,
  AudioLines,
  Search,
  ArrowRight,
} from "lucide-react";

import "@/styles/console-theme.css";

export default function DashboardPage() {
  const stats = useDashboardStats();

  // Purely cosmetic live clock for the console header - client-only to
  // avoid SSR/client markup mismatches, doesn't touch any data fetching.
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <MainLayout>
      <div className="console-theme -m-8 min-h-[calc(100%+4rem)] p-8">
        {/* Header */}
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-console-display text-3xl font-semibold tracking-tight text-foreground">
              Welcome back, Alex
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Here&apos;s what&apos;s happening with your creator journey today.
            </p>
          </div>
          {now ? (
            <span className="font-console-mono rounded-lg border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground">
              {now.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" }).toUpperCase()}{" "}
              <span className="text-primary">{now.toLocaleTimeString()}</span>
            </span>
          ) : null}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-6">
          <StatsCard
            title="Projects"
            value={stats.projects}
            description="Active projects"
            icon={<FolderKanban className="h-6 w-6 text-blue-400" />}
            loading={stats.isLoading}
            href="/projects"
          />
          <StatsCard
            title="Scripts"
            value={stats.scripts}
            description="Generated scripts"
            icon={<FileText className="h-6 w-6 text-green-400" />}
            loading={stats.isLoading}
            href="/scripts"
          />
          <StatsCard
            title="Videos"
            value={stats.videos}
            description="Videos created"
            icon={<Video className="h-6 w-6 text-purple-400" />}
            loading={stats.isLoading}
            href="/videos"
          />
          <StatsCard
            title="Images"
            value={stats.images}
            description="Images generated"
            icon={<ImageIcon className="h-6 w-6 text-pink-400" />}
            loading={stats.isLoading}
            href="/thumbnails"
          />
          <StatsCard
            title="Audio"
            value={stats.audio}
            description="Audio tracks"
            icon={<AudioLines className="h-6 w-6 text-cyan-400" />}
            loading={stats.isLoading}
            href="/assets"
          />
          <StatsCard
            title="Credits"
            value={stats.credits}
            description="Credits remaining"
            icon={<Coins className="h-6 w-6 text-yellow-400" />}
            loading={stats.isLoading}
            href="/billing"
          />
        </div>

        {/* Command Center entry point - same destination/behavior as before (Link to /command-center),
            just restyled to look like an inline console prompt instead of a gradient banner. */}
        <Link
          href="/command-center"
          className="console-glow mt-6 flex w-full items-center gap-3 rounded-2xl border border-border bg-card px-5 py-4 text-left shadow-sm transition-colors hover:border-primary/40"
        >
          <Search className="h-4 w-4 shrink-0 text-primary" />
          <span className="flex-1 truncate text-sm text-muted-foreground">
            Ask CreatorOS AI to create something&hellip; a script, thumbnail, video, or SEO pack
          </span>
          <span className="font-console-mono shrink-0 rounded-md border border-border px-2.5 py-1 text-[11px] text-primary">
            Open Command Center
          </span>
          <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground" />
        </Link>

        <div className="mt-8">
          <QuickActions />
        </div>

        <div className="mt-8">
          <RecentProjects />
        </div>
      </div>
    </MainLayout>
  );
}