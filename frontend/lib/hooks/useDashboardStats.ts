"use client";

import { useEffect, useState } from "react";
import { listProjects } from "@/features/projects/services/project.service";
import { getDashboardStats } from "@/lib/services/dashboard.service";

export interface DashboardData {
  projects: number;
  scripts: number;
  videos: number;
  images: number;
  audio: number;
  credits: number;
  isLoading: boolean;
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
  });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const [projects, stats] = await Promise.all([
        listProjects().catch(() => []),
        getDashboardStats(),
      ]);

      if (cancelled) return;

      setData({
        projects: projects.length,
        scripts: stats.scripts,
        videos: stats.videos,
        images: stats.images,
        audio: stats.audio,
        credits: stats.credits,
        isLoading: false,
      });
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}