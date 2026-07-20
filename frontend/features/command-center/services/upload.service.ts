import apiClient from "@/lib/api/client";

export interface UploadResult {
  assetId: string;
  fileUrl: string;
  kind: "image" | "video" | "audio" | "document";
}

export async function uploadFile(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post("/api/v1/uploads", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return {
    assetId: data.asset_id,
    fileUrl: data.file_url,
    kind: data.kind,
  };
}