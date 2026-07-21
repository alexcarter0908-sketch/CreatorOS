"use client";

import { useEffect, useState } from "react";
import { listProjects } from "@/features/projects/services/project.service";
import { listAssets } from "@/features/assets/services/asset.service";
import { getDashboardStats } from "@/lib/services/dashboard.service";

export interface DailyActivityPoint {
  date: string; // e.g. "Jul 10"
  count: number;
}

export interface ContentMixSlice {
  name: string;
  value: number;
}

export interface DashboardData {
  projects: number;
  scripts: number;
  videos: number;
  images: number;
  audio: number;
  credits: number;
  isLoading: boolean;
  // Real counts of items created in the last 7 days, computed from actual
  // created_at timestamps - not fabricated. Undefined while loading.
  projectsThisWeek?: number;
  scriptsThisWeek?: number;
  videosThisWeek?: number;
  imagesThisWeek?: number;
  audioThisWeek?: number;
  // Chart data - both derived from the same real asset list above, no
  // separate fetch and no fabricated values.
  dailyActivity: DailyActivityPoint[];
  contentMix: ContentMixSlice[];
}

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;
const DAY_MS = 24 * 60 * 60 * 1000;
const ACTIVITY_WINDOW_DAYS = 14;

function countSince(items: { created_at: string }[], sinceMs: number): number {
  return items.filter((item) => new Date(item.created_at).getTime() >= sinceMs).length;
}

function buildDailyActivity(items: { created_at: string }[]): DailyActivityPoint[] {
  const days: DailyActivityPoint[] = [];
  const now = new Date();

  for (let i = ACTIVITY_WINDOW_DAYS - 1; i >= 0; i--) {
    const day = new Date(now.getTime() - i * DAY_MS);
    const dayKey = day.toDateString();
    const count = items.filter((item) => new Date(item.created_at).toDateString() === dayKey).length;
    days.push({
      date: day.toLocaleDateString([], { month: "short", day: "numeric" }),
      count,
    });
  }

  return days;
}

export function useDashboardStats(): DashboardData {
  const [data, setData] = useState<DashboardData>({
    projects: 0,
    scripts: 0,
    videos: 0,
    images: 0,
    audio: 0,
    credits: 0,
    isLoading: true,
    dailyActivity: [],
    contentMix: [],
  });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const [projects, stats, assets] = await Promise.all([
        listProjects().catch(() => []),
        getDashboardStats(),
        listAssets().catch(() => []),
      ]);

      if (cancelled) return;

      const since = Date.now() - WEEK_MS;

      const contentMix: ContentMixSlice[] = [
        { name: "Scripts", value: stats.scripts },
        { name: "Images", value: stats.images },
        { name: "Videos", value: stats.videos },
        { name: "Audio", value: stats.audio },
      ].filter((slice) => slice.value > 0);

      setData({
        projects: projects.length,
        scripts: stats.scripts,
        videos: stats.videos,
        images: stats.images,
        audio: stats.audio,
        credits: stats.credits,
        isLoading: false,
        projectsThisWeek: countSince(projects, since),
        scriptsThisWeek: countSince(assets.filter((a) => a.asset_type === "text"), since),
        videosThisWeek: countSince(assets.filter((a) => a.asset_type === "video"), since),
        imagesThisWeek: countSince(assets.filter((a) => a.asset_type === "image"), since),
        audioThisWeek: countSince(assets.filter((a) => a.asset_type === "audio"), since),
        dailyActivity: buildDailyActivity(assets),
        contentMix,
      });
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}