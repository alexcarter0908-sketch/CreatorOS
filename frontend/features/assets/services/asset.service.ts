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