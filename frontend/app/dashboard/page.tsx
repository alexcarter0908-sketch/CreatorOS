"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import MainLayout from "@/components/layout/MainLayout";
import BrandWatermark from "@/components/common/BrandWatermark";
import StatsCard from "@/components/dashboard/StatsCard";
import QuickActions from "@/components/dashboard/QuickActions";
import RecentProjects from "@/components/dashboard/RecentProjects";
import ContentPipeline from "@/components/dashboard/ContentPipeline";
import RecentActivity from "@/components/dashboard/RecentActivity";
import AssetLibrary from "@/components/dashboard/AssetLibrary";
import AnalyticsSnapshot from "@/components/dashboard/AnalyticsSnapshot";

import { useDashboardStats } from "@/lib/hooks/useDashboardStats";
import { useAuthStore } from "@/features/auth/store/auth.store";

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
  const user = useAuthStore((state) => state.user);
  const firstName = user?.full_name?.trim().split(/\s+/)[0] || "there";

  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <MainLayout>
      <div className="console-theme relative isolate -m-8 min-h-[calc(100%+4rem)] overflow-hidden p-8">
        <BrandWatermark />
        <div className="relative z-10">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-console-display text-3xl font-semibold tracking-tight text-foreground">
              Welcome back, {firstName}
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

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-6">
          <StatsCard
            title="Projects"
            value={stats.projects}
            description="Active projects"
            icon={<FolderKanban className="h-6 w-6 text-blue-400" />}
            loading={stats.isLoading}
            href="/projects"
            trendThisWeek={stats.projectsThisWeek}
          />
          <StatsCard
            title="Scripts"
            value={stats.scripts}
            description="Generated scripts"
            icon={<FileText className="h-6 w-6 text-green-400" />}
            loading={stats.isLoading}
            href="/scripts"
            trendThisWeek={stats.scriptsThisWeek}
          />
          <StatsCard
            title="Videos"
            value={stats.videos}
            description="Videos created"
            icon={<Video className="h-6 w-6 text-purple-400" />}
            loading={stats.isLoading}
            href="/videos"
            trendThisWeek={stats.videosThisWeek}
          />
          <StatsCard
            title="Images"
            value={stats.images}
            description="Images generated"
            icon={<ImageIcon className="h-6 w-6 text-pink-400" />}
            loading={stats.isLoading}
            href="/thumbnails"
            trendThisWeek={stats.imagesThisWeek}
          />
          <StatsCard
            title="Audio"
            value={stats.audio}
            description="Audio tracks"
            icon={<AudioLines className="h-6 w-6 text-cyan-400" />}
            loading={stats.isLoading}
            href="/assets"
            trendThisWeek={stats.audioThisWeek}
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
          <AnalyticsSnapshot
            dailyActivity={stats.dailyActivity}
            contentMix={stats.contentMix}
            isLoading={stats.isLoading}
          />
        </div>

        <div className="mt-8">
          <QuickActions />
        </div>

        <div className="mt-8">
          <ContentPipeline />
        </div>

        <div className="mt-8 grid grid-cols-1 gap-6 xl:grid-cols-[1.15fr_1fr]">
          <RecentActivity />
          <AssetLibrary
            scripts={stats.scripts}
            images={stats.images}
            videos={stats.videos}
            audio={stats.audio}
            isLoading={stats.isLoading}
          />
        </div>

        <div className="mt-8">
          <RecentProjects />
        </div>
        </div>
      </div>
    </MainLayout>
  );
}
