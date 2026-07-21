export type AutoTargetAssetType = "text" | "image" | "video" | "audio";

export interface AutoTarget {
  id: string;
  asset_type: AutoTargetAssetType;
  prompt: string;
  project_id: string | null;
  interval_days: number;
  run_at_hour: number;
  run_at_minute: number;
  auto_publish: boolean;
  platforms: string | null;
  tags: string | null;
  is_active: boolean;
  last_run_at: string | null;
  last_run_date: string | null;
}

export interface CreateAutoTargetPayload {
  asset_type: AutoTargetAssetType;
  prompt: string;
  project_id?: string | null;
  interval_days: number;
  run_at_hour: number;
  run_at_minute: number;
  auto_publish: boolean;
  platforms?: string[];
  tags?: string[];
}