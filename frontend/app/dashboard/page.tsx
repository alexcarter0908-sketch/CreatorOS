"use client";

import Link from "next/link";

import MainLayout from "@/components/layout/MainLayout";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import StatsCard from "@/components/dashboard/StatsCard";
import QuickActions from "@/components/dashboard/QuickActions";
import RecentProjects from "@/components/dashboard/RecentProjects";

import { useDashboardStats } from "@/lib/hooks/useDashboardStats";

import { FolderKanban, FileText, Video, Coins, Terminal, ArrowRight } from "lucide-react";

export default function DashboardPage() {
  const stats = useDashboardStats();

  return (
    <MainLayout>
      <DashboardHeader title="Dashboard" subtitle="Welcome back to CreatorOS" />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatsCard
          title="Projects"
          value={stats.projects}
          description="Active projects"
          icon={<FolderKanban className="h-7 w-7 text-blue-600" />}
          loading={stats.isLoading}
        />

        <StatsCard
          title="Scripts"
          value={stats.scripts}
          description="Generated scripts"
          icon={<FileText className="h-7 w-7 text-green-600" />}
          loading={stats.isLoading}
        />

        <StatsCard
          title="Videos"
          value={stats.videos}
          description="Videos created"
          icon={<Video className="h-7 w-7 text-purple-600" />}
          loading={stats.isLoading}
        />

        <StatsCard
          title="Credits"
          value={stats.credits}
          description="Credits remaining"
          icon={<Coins className="h-7 w-7 text-yellow-600" />}
          loading={stats.isLoading}
        />
      </div>

      <div className="mt-8">
        <QuickActions />
      </div>

      <div className="mt-8">
        <RecentProjects />
      </div>

      <div className="mt-8 rounded-2xl border border-border bg-gradient-to-br from-slate-900 to-slate-800 p-8 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-card/10">
            <Terminal className="h-6 w-6 text-white" />
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white">Command Center</h2>
            <p className="mt-1 text-base text-slate-300">
              Control CreatorOS using natural language commands.
            </p>
          </div>
        </div>

        <div className="mt-6">
          <Link
            href="/command-center"
            className="inline-flex items-center gap-2 rounded-xl bg-card px-5 py-3 text-base font-medium text-foreground transition hover:bg-muted"
          >
            Open Command Center
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </MainLayout>
  );
}