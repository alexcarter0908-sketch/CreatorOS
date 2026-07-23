import apiClient from "@/lib/api/client";
import type { Asset, AssetType } from "../types/asset";

export async function listAssets(assetType?: AssetType, limit?: number): Promise<Asset[]> {
  const { data } = await apiClient.get<Asset[]>("/api/v1/assets", {
    params: {
      ...(assetType ? { asset_type: assetType } : {}),
      ...(limit ? { limit } : {}),
    },
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

function filenameFromContentDisposition(
  header: string | undefined,
  fallback: string
): string {
  if (!header) return fallback;
  const match = header.match(/filename="?([^";]+)"?/i);
  return match ? match[1] : fallback;
}

export async function downloadAsset(assetId: string): Promise<void> {
  const response = await apiClient.get(`/api/v1/publish/download/${assetId}`, {
    responseType: "blob",
  });

  const filename = filenameFromContentDisposition(
    response.headers["content-disposition"],
    `creatoros_${assetId}`
  );

  const blobUrl = window.URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(blobUrl);
}