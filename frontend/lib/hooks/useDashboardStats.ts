"use client";

import { useEffect, useState } from "react";
import { listProjects } from "@/features/projects/services/project.service";
import { listAssets } from "@/features/assets/services/asset.service";
import { getDashboardStats } from "@/lib/services/dashboard.service";
import type { Asset } from "@/features/assets/types/asset";

export interface DailyActivityPoint {
  date: string; // e.g. "Jul 10"
  count: number;
}

export interface DailyTypeBreakdownPoint {
  date: string;
  scripts: number;
  videos: number;
  images: number;
  audio: number;
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
  // Chart data - all derived from the same real asset/project lists above,
  // no separate fetch and no fabricated values.
  dailyActivity: DailyActivityPoint[];
  dailyActivityByType: DailyTypeBreakdownPoint[];
  contentMix: ContentMixSlice[];
  // Last-7-day per-category counts, for the small sparkline on each stat
  // card. Same source data as everything else above.
  projectsSparkline: number[];
  scriptsSparkline: number[];
  videosSparkline: number[];
  imagesSparkline: number[];
  audioSparkline: number[];
}

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;
const DAY_MS = 24 * 60 * 60 * 1000;
const ACTIVITY_WINDOW_DAYS = 14;
const SPARKLINE_WINDOW_DAYS = 7;

function countSince(items: { created_at: string }[], sinceMs: number): number {
  return items.filter((item) => new Date(item.created_at).getTime() >= sinceMs).length;
}

function dayKeys(windowDays: number): { key: string; label: string }[] {
  const days: { key: string; label: string }[] = [];
  const now = new Date();
  for (let i = windowDays - 1; i >= 0; i--) {
    const day = new Date(now.getTime() - i * DAY_MS);
    days.push({
      key: day.toDateString(),
      label: day.toLocaleDateString([], { month: "short", day: "numeric" }),
    });
  }
  return days;
}

function buildDailyActivity(items: { created_at: string }[]): DailyActivityPoint[] {
  return dayKeys(ACTIVITY_WINDOW_DAYS).map(({ key, label }) => ({
    date: label,
    count: items.filter((item) => new Date(item.created_at).toDateString() === key).length,
  }));
}

function buildDailyActivityByType(assets: Asset[]): DailyTypeBreakdownPoint[] {
  return dayKeys(ACTIVITY_WINDOW_DAYS).map(({ key, label }) => {
    const sameDay = assets.filter((a) => new Date(a.created_at).toDateString() === key);
    return {
      date: label,
      scripts: sameDay.filter((a) => a.asset_type === "text").length,
      videos: sameDay.filter((a) => a.asset_type === "video").length,
      images: sameDay.filter((a) => a.asset_type === "image").length,
      audio: sameDay.filter((a) => a.asset_type === "audio").length,
    };
  });
}

function buildSparkline(items: { created_at: string }[]): number[] {
  return dayKeys(SPARKLINE_WINDOW_DAYS).map(
    ({ key }) => items.filter((item) => new Date(item.created_at).toDateString() === key).length
  );
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
    dailyActivityByType: [],
    contentMix: [],
    projectsSparkline: [],
    scriptsSparkline: [],
    videosSparkline: [],
    imagesSparkline: [],
    audioSparkline: [],
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

      const scriptAssets = assets.filter((a) => a.asset_type === "text");
      const videoAssets = assets.filter((a) => a.asset_type === "video");
      const imageAssets = assets.filter((a) => a.asset_type === "image");
      const audioAssets = assets.filter((a) => a.asset_type === "audio");

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
        scriptsThisWeek: countSince(scriptAssets, since),
        videosThisWeek: countSince(videoAssets, since),
        imagesThisWeek: countSince(imageAssets, since),
        audioThisWeek: countSince(audioAssets, since),
        dailyActivity: buildDailyActivity(assets),
        dailyActivityByType: buildDailyActivityByType(assets),
        contentMix,
        projectsSparkline: buildSparkline(projects),
        scriptsSparkline: buildSparkline(scriptAssets),
        videosSparkline: buildSparkline(videoAssets),
        imagesSparkline: buildSparkline(imageAssets),
        audioSparkline: buildSparkline(audioAssets),
      });
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}