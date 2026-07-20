export type AutoTargetAssetType = "text" | "image" | "video" | "audio";

export interface AutoTarget {
  id: string;
  asset_type: AutoTargetAssetType;
  prompt: string;
  project_id: string | null;
  frequency_hours: number;
  is_active: boolean;
  last_run_at: string | null;
}

export interface CreateAutoTargetPayload {
  asset_type: AutoTargetAssetType;
  prompt: string;
  project_id?: string | null;
  frequency_hours: number;
}