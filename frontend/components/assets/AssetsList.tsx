"use client";

import { useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileWarning,
  Loader2,
  Pencil,
  RefreshCw,
  Save,
  Trash2,
  Video,
  X,
} from "lucide-react";

import MainLayout from "@/components/layout/MainLayout";
import {
  deleteAsset,
  generateVideoFromScript,
  listAssets,
  retryAsset,
  updateAssetText,
} from "@/features/assets/services/asset.service";
import type { Asset, AssetType } from "@/features/assets/types/asset";
import PublishToYouTubeButton from "@/components/publishing/PublishToYouTubeButton";

const STATUS_CONFIG = {
  pending: { label: "Pending", className: "bg-yellow-100 text-yellow-700", icon: Clock },
  completed: { label: "Completed", className: "bg-green-100 text-green-700", icon: CheckCircle2 },
  failed: { label: "Failed", className: "bg-red-100 text-red-700", icon: AlertCircle },
};

const TEXT_LIKE_TYPES: AssetType[] = ["text", "seo", "script", "document"];

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

  // Per-card UI state, keyed by asset id.
  const [editingId, setEditingId] = useState(null as string | null);
  const [draftText, setDraftText] = useState("");
  const [busyId, setBusyId] = useState(null as string | null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null as string | null);
  const [actionError, setActionError] = useState(null as string | null);
  const [videoStartedId, setVideoStartedId] = useState(null as string | null);

  const isTextLike = TEXT_LIKE_TYPES.includes(assetType);
  // "Make Video" only makes sense for actual scripts (asset_type "text"),
  // not SEO/document text - those aren't meant to become videos.
  const canMakeVideo = assetType === "text";

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

  function startEdit(asset: Asset) {
    setActionError(null);
    setEditingId(asset.id);
    setDraftText(getGeneratedText(asset) ?? "");
  }

  function cancelEdit() {
    setEditingId(null);
    setDraftText("");
  }

  async function saveEdit(asset: Asset) {
    setActionError(null);
    setBusyId(asset.id);
    try {
      const updated = await updateAssetText(asset.id, draftText);
      setAssets((prev) => prev.map((a) => (a.id === asset.id ? updated : a)));
      setEditingId(null);
      setDraftText("");
    } catch {
      setActionError("Couldn't save your changes. Please try again.");
    } finally {
      setBusyId(null);
    }
  }

  async function handleRetryOrRewrite(asset: Asset) {
    setActionError(null);
    setBusyId(asset.id);
    // Show it as pending immediately while regeneration runs.
    setAssets((prev) =>
      prev.map((a) => (a.id === asset.id ? { ...a, status: "pending" } : a))
    );
    try {
      const updated = await retryAsset(asset.id);
      setAssets((prev) => prev.map((a) => (a.id === asset.id ? updated : a)));
    } catch {
      setActionError("Regeneration failed. Please try again.");
      setAssets((prev) =>
        prev.map((a) => (a.id === asset.id ? { ...a, status: "failed" } : a))
      );
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(asset: Asset) {
    setActionError(null);
    setBusyId(asset.id);
    try {
      await deleteAsset(asset.id);
      setAssets((prev) => prev.filter((a) => a.id !== asset.id));
    } catch {
      setActionError("Couldn't delete this item. Please try again.");
    } finally {
      setBusyId(null);
      setConfirmDeleteId(null);
    }
  }

  async function handleMakeVideo(asset: Asset) {
    setActionError(null);
    setBusyId(asset.id);
    try {
      await generateVideoFromScript(asset.id);
      setVideoStartedId(asset.id);
    } catch {
      setActionError("Couldn't start video generation. Please try again.");
    } finally {
      setBusyId(null);
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
      {actionError && (
        <p className="mb-3 text-sm text-red-500">{actionError}</p>
      )}

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
          const isEditing = editingId === asset.id;
          const isBusy = busyId === asset.id;
          const canEdit = isTextLike && asset.status === "completed" && !isEditing;

          return (
            <div key={asset.id} className="rounded-xl border bg-card p-5 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {asset.prompt ?? "(no prompt)"}
                </p>

                <span className={"flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold " + config.className}>
                  {isBusy ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <StatusIcon className="h-3.5 w-3.5" />
                  )}
                  {isBusy ? "Working..." : config.label}
                </span>
              </div>

              {isEditing ? (
                <div className="mt-2">
                  <textarea
                    value={draftText}
                    onChange={(e) => setDraftText(e.target.value)}
                    rows={6}
                    className="w-full rounded-lg border p-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                    placeholder="Edit the generated text..."
                  />
                </div>
              ) : (
                <>
                  {generatedText && (
                    <p className="mt-2 whitespace-pre-wrap text-sm text-foreground">
                      {generatedText}
                    </p>
                  )}

                  {!generatedText && asset.status === "pending" && (
                    <p className="mt-2 text-sm text-muted-foreground">Generating...</p>
                  )}
                </>
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

              {videoStartedId === asset.id && (
                <div className="mt-3 flex items-start gap-2 rounded-lg bg-green-50 p-3 text-xs text-green-700">
                  <Video className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>
                    Video generation started using this script. Check the{" "}
                    <a href="/videos" className="font-semibold underline">
                      Videos
                    </a>{" "}
                    page in a bit for the result.
                  </span>
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

              {/* ---- Action bar: edit / rewrite / retry / delete ---- */}
              <div className="mt-4 flex flex-wrap items-center gap-2 border-t pt-3">
                {isEditing ? (
                  <>
                    <button
                      type="button"
                      disabled={isBusy}
                      onClick={() => saveEdit(asset)}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50"
                    >
                      <Save className="h-3.5 w-3.5" />
                      Save
                    </button>
                    <button
                      type="button"
                      disabled={isBusy}
                      onClick={cancelEdit}
                      className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted disabled:opacity-50"
                    >
                      <X className="h-3.5 w-3.5" />
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    {canEdit && (
                      <button
                        type="button"
                        disabled={isBusy}
                        onClick={() => startEdit(asset)}
                        className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted disabled:opacity-50"
                      >
                        <Pencil className="h-3.5 w-3.5" />
                        Edit
                      </button>
                    )}

                    {asset.status === "completed" && (
                      <button
                        type="button"
                        disabled={isBusy}
                        onClick={() => handleRetryOrRewrite(asset)}
                        className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted disabled:opacity-50"
                      >
                        <RefreshCw className="h-3.5 w-3.5" />
                        Rewrite
                      </button>
                    )}

                    {canMakeVideo && asset.status === "completed" && (
                      <button
                        type="button"
                        disabled={isBusy}
                        onClick={() => handleMakeVideo(asset)}
                        className="inline-flex items-center gap-1.5 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
                      >
                        <Video className="h-3.5 w-3.5" />
                        Make Video
                      </button>
                    )}

                    {asset.status === "failed" && (
                      <button
                        type="button"
                        disabled={isBusy}
                        onClick={() => handleRetryOrRewrite(asset)}
                        className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted disabled:opacity-50"
                      >
                        <RefreshCw className="h-3.5 w-3.5" />
                        Retry
                      </button>
                    )}

                    {confirmDeleteId === asset.id ? (
                      <span className="inline-flex items-center gap-2 text-xs">
                        <span className="text-muted-foreground">Delete this?</span>
                        <button
                          type="button"
                          disabled={isBusy}
                          onClick={() => handleDelete(asset)}
                          className="rounded-lg bg-red-600 px-2.5 py-1 font-semibold text-white hover:bg-red-700 disabled:opacity-50"
                        >
                          Yes, delete
                        </button>
                        <button
                          type="button"
                          disabled={isBusy}
                          onClick={() => setConfirmDeleteId(null)}
                          className="rounded-lg border px-2.5 py-1 font-semibold hover:bg-muted disabled:opacity-50"
                        >
                          Cancel
                        </button>
                      </span>
                    ) : (
                      <button
                        type="button"
                        disabled={isBusy}
                        onClick={() => setConfirmDeleteId(asset.id)}
                        className="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50 disabled:opacity-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Delete
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </MainLayout>
  );
}
