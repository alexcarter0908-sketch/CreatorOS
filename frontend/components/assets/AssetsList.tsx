"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Clock, Download, FileWarning, Trash2 } from "lucide-react";
import { toast } from "sonner";

import MainLayout from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { deleteAsset, downloadAsset, listAssets } from "@/features/assets/services/asset.service";
import type { Asset, AssetType } from "@/features/assets/types/asset";
import PublishToYouTubeButton from "@/components/publishing/PublishToYouTubeButton";

const STATUS_CONFIG = {
  pending: { label: "Pending", className: "bg-yellow-100 text-yellow-700", icon: Clock },
  completed: { label: "Completed", className: "bg-green-100 text-green-700", icon: CheckCircle2 },
  failed: { label: "Failed", className: "bg-red-100 text-red-700", icon: AlertCircle },
};

interface AssetsListProps {
  assetType: AssetType;
  title: string;
  subtitle: string;
}

function getGeneratedText(asset: Asset): string | null {
  const meta = asset.extra_metadata;
  if (meta && typeof meta === "object" && "text" in meta) {
    const value = (meta as Record<string, unknown>).text;
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }
  return null;
}

export default function AssetsList({ assetType, title, subtitle }: AssetsListProps) {
  const [assets, setAssets] = useState([] as Asset[]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null as string | null);
  const [downloadingId, setDownloadingId] = useState(null as string | null);
  const [deletingId, setDeletingId] = useState(null as string | null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await listAssets(assetType);
        if (!cancelled) setAssets(data);
      } catch {
        if (!cancelled) setError("Failed to load assets.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [assetType]);

  async function handleDownload(asset: Asset) {
    setDownloadingId(asset.id);
    try {
      await downloadAsset(asset.id);
    } catch {
      toast.error("Failed to download file.");
    } finally {
      setDownloadingId(null);
    }
  }

  async function handleDelete(asset: Asset) {
    setDeletingId(asset.id);
    try {
      await deleteAsset(asset.id);
      setAssets((prev) => prev.filter((a) => a.id !== asset.id));
      toast.success("Deleted.");
    } catch {
      toast.error("Failed to delete.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <MainLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">{title}</h1>
        <p className="mt-2 text-muted-foreground">{subtitle}</p>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {!isLoading && !error && assets.length === 0 && (
        <div className="rounded-xl border border-dashed p-10 text-center text-sm text-muted-foreground">
          Nothing generated yet. Use the Command Center to create one.
        </div>
      )}

      <div className="space-y-3">
        {assets.map((asset) => {
          const config = STATUS_CONFIG[asset.status] ?? STATUS_CONFIG.pending;
          const StatusIcon = config.icon;
          const fileUrl = asset.file_url;
          const generatedText = getGeneratedText(asset);

          return (
            <div key={asset.id} className="rounded-xl border bg-card p-5 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {asset.prompt ?? "(no prompt)"}
                </p>

                <div className="flex shrink-0 items-center gap-2">
                  <span className={"flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold " + config.className}>
                    <StatusIcon className="h-3.5 w-3.5" />
                    {config.label}
                  </span>

                  {fileUrl && (
                    <Button
                      variant="outline"
                      size="icon-sm"
                      aria-label="Download"
                      disabled={downloadingId === asset.id}
                      onClick={() => handleDownload(asset)}
                    >
                      <Download className="h-3.5 w-3.5" />
                    </Button>
                  )}

                  <Button
                    variant="destructive"
                    size="icon-sm"
                    aria-label="Delete"
                    disabled={deletingId === asset.id}
                    onClick={() => handleDelete(asset)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {generatedText && (
                <p className="mt-2 whitespace-pre-wrap text-sm text-foreground">
                  {generatedText}
                </p>
              )}

              {!generatedText && asset.status === "pending" && (
                <p className="mt-2 text-sm text-muted-foreground">Generating...</p>
              )}

              <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                <span>{asset.provider} / {asset.model_id}</span>
                <span>{new Date(asset.created_at).toLocaleString()}</span>
              </div>

              {asset.status === "failed" && asset.error_message && (
                <div className="mt-3 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-xs text-red-600">
                  <FileWarning className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{asset.error_message}</span>
                </div>
              )}

              {fileUrl ? (
                assetType === "image" ? (
                  <img
                    src={fileUrl}
                    alt={asset.prompt ?? "Generated image"}
                    className="mt-3 max-h-64 rounded-lg border object-cover"
                  />
                ) : assetType === "video" ? (
                  <video
                    src={fileUrl}
                    controls
                    className="mt-3 max-h-64 w-full rounded-lg border"
                  />
                ) : assetType === "audio" ? (
                  <audio src={fileUrl} controls className="mt-3 w-full" />
                ) : (
                  <a href={fileUrl} target="_blank" rel="noreferrer" className="mt-3 inline-block text-xs font-medium text-blue-600 hover:underline">
                    View asset
                  </a>
                )
              ) : null}
              {assetType === "video" ? (
                <div className="mt-3">
                  <PublishToYouTubeButton assetId={asset.id} defaultTitle={asset.prompt ?? "CreatorOS video"} />
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </MainLayout>
  );
}