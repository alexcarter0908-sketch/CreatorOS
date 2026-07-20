import apiClient from "@/lib/api/client";

export interface DashboardStats {
  scripts: number;
  videos: number;
  images: number;
  audio: number;
  credits: number;
}

const EMPTY_STATS: DashboardStats = {
  scripts: 0,
  videos: 0,
  images: 0,
  audio: 0,
  credits: 0,
};

export async function getDashboardStats(): Promise<DashboardStats> {
  try {
    const { data } = await apiClient.get<DashboardStats>("/api/v1/assets/stats");
    return data;
  } catch {
    return EMPTY_STATS;
  }
}