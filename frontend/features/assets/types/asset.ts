export type AssetType = "text" | "image" | "video" | "audio" | "seo" | "script" | "document";
export type AssetStatus = "pending" | "completed" | "failed";

export interface Asset {
  id: string;
  project_id: string | null;
  asset_type: AssetType;
  provider: string;
  model_id: string;
  prompt: string | null;
  status: AssetStatus;
  file_url: string | null;
  extra_metadata: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}