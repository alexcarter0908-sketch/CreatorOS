import apiClient from "@/lib/api/client";

export interface DashboardStats {
  scripts: number;
  videos: number;
  images: number;
  audio: number;
  credits: number;
}

export interface WeeklyCounts {
  scripts: number;
  videos: number;
  images: number;
  audio: number;
}

export interface DailyActivityPoint {
  date: string;
  count: number;
}

export interface AssetActivity {
  weekly: WeeklyCounts;
  daily_activity: DailyActivityPoint[];
}

const EMPTY_STATS: DashboardStats = {
  scripts: 0,
  videos: 0,
  images: 0,
  audio: 0,
  credits: 0,
};

const EMPTY_ACTIVITY: AssetActivity = {
  weekly: { scripts: 0, videos: 0, images: 0, audio: 0 },
  daily_activity: [],
};

export async function getDashboardStats(): Promise<DashboardStats> {
  try {
    const { data } = await apiClient.get<DashboardStats>("/api/v1/assets/stats");
    return data;
  } catch {
    return EMPTY_STATS;
  }
}

export async function getAssetActivity(days = 14): Promise<AssetActivity> {
  try {
    const { data } = await apiClient.get<AssetActivity>("/api/v1/assets/activity", {
      params: { days },
    });
    return data;
  } catch {
    return EMPTY_ACTIVITY;
  }
}