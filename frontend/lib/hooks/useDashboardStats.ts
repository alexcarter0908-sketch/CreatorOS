"use client";

import { useCallback, useEffect, useState } from "react";
import { listProjects } from "@/features/projects/services/project.service";
import { getAssetActivity, getDashboardStats } from "@/lib/services/dashboard.service";

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
  // Real counts of items created in the last 7 days, computed server-side
  // from the user's full history (not capped to a page of recent items).
  // Undefined while loading.
  projectsThisWeek?: number;
  scriptsThisWeek?: number;
  videosThisWeek?: number;
  imagesThisWeek?: number;
  audioThisWeek?: number;
  // Chart data - both come from lightweight, purpose-built aggregate
  // endpoints, not a full asset list fetched just to compute this client-side.
  dailyActivity: DailyActivityPoint[];
  contentMix: ContentMixSlice[];
  // For fix #5: lets the dashboard show "Updated Xm ago" and offer a
  // manual refresh without a full page reload.
  lastUpdated: Date | null;
  refresh: () => void;
}

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

function countSince(items: { created_at: string }[], sinceMs: number): number {
  return items.filter((item) => new Date(item.created_at).getTime() >= sinceMs).length;
}

function formatShortDate(isoDate: string): string {
  // isoDate is "YYYY-MM-DD" from the backend. Append a time so this
  // parses as local midnight rather than UTC midnight, which can shift
  // the displayed day by one depending on the viewer's timezone.
  const d = new Date(`${isoDate}T00:00:00`);
  return d.toLocaleDateString([], { month: "short", day: "numeric" });
}

export function useDashboardStats(): DashboardData {
  const [data, setData] = useState<Omit<DashboardData, "refresh">>({
    projects: 0,
    scripts: 0,
    videos: 0,
    images: 0,
    audio: 0,
    credits: 0,
    isLoading: true,
    dailyActivity: [],
    contentMix: [],
    lastUpdated: null,
  });
  const [reloadToken, setReloadToken] = useState(0);

  const refresh = useCallback(() => setReloadToken((t) => t + 1), []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const [projects, stats, activity] = await Promise.all([
        listProjects().catch(() => []),
        getDashboardStats(),
        getAssetActivity(14),
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
        scriptsThisWeek: activity.weekly.scripts,
        videosThisWeek: activity.weekly.videos,
        imagesThisWeek: activity.weekly.images,
        audioThisWeek: activity.weekly.audio,
        dailyActivity: activity.daily_activity.map((point) => ({
          date: formatShortDate(point.date),
          count: point.count,
        })),
        contentMix,
        lastUpdated: new Date(),
      });
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  return { ...data, refresh };
}