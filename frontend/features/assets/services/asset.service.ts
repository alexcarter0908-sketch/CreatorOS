import apiClient from "@/lib/api/client";
import type { Asset, AssetType } from "../types/asset";

export async function listAssets(assetType?: AssetType): Promise<Asset[]> {
  const { data } = await apiClient.get<Asset[]>("/api/v1/assets", {
    params: assetType ? { asset_type: assetType } : undefined,
  });
  return data;
}

export async function getAsset(id: string): Promise<Asset> {
  const { data } = await apiClient.get<Asset>("/api/v1/assets/" + id);
  return data;
}

export async function deleteAsset(id: string): Promise<void> {
  await apiClient.delete("/api/v1/assets/" + id);
}

export async function updateAssetText(id: string, text: string): Promise<Asset> {
  const { data } = await apiClient.patch<Asset>("/api/v1/assets/" + id, { text });
  return data;
}

export async function retryAsset(id: string, prompt?: string): Promise<Asset> {
  const { data } = await apiClient.post<Asset>(
    "/api/v1/assets/" + id + "/retry",
    prompt ? { prompt } : {}
  );
  return data;
}

export interface GenerateVideoResponse {
  workflow_id: string;
  status: string;
  source_asset_id: string;
}

export async function generateVideoFromScript(id: string): Promise<GenerateVideoResponse> {
  const { data } = await apiClient.post<GenerateVideoResponse>(
    "/api/v1/assets/" + id + "/generate-video"
  );
  return data;
}