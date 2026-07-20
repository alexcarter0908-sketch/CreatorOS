$assetsContent = @'
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ArrowLeft, Copy, Download, FileText, Loader2, RefreshCw, Trash2 } from "lucide-react";
import apiClient from "@/lib/api/client";

interface LibraryAsset {
  id: string;
  asset_type: string;
  status: string;
  prompt?: string | null;
  file_url?: string | null;
  extra_metadata?: Record<string, unknown> | null;
  created_at: string;
}

const TYPE_FILTERS = [
  { value: "", label: "All" },
  { value: "video", label: "Video" },
  { value: "image", label: "Image" },
  { value: "audio", label: "Audio" },
  { value: "text", label: "Script" },
  { value: "document", label: "Document" },
  { value: "seo", label: "SEO" },
];

function getAssetText(asset: LibraryAsset): string {
  const meta = asset.extra_metadata ?? {};
  const text = meta.text;
  const raw = meta.raw_result;
  if (typeof text === "string" && text) return text;
  if (typeof raw === "string" && raw) return raw;
  return "";
}

function AssetCard({ asset, onDelete }: { asset: LibraryAsset; onDelete: (id: string) => void }) {
  const text = getAssetText(asset);
  const [deleting, setDeleting] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(text || asset.prompt || "");
    toast.success("Copied to clipboard.");
  }

  async function handleDelete() {
    if (!window.confirm("Delete this asset? This can't be undone.")) return;
    setDeleting(true);
    try {
      await apiClient.delete(`/api/v1/assets/${asset.id}`);
      toast.success("Asset deleted.");
      onDelete(asset.id);
    } catch {
      toast.error("Could not delete this asset. Please try again.");
      setDeleting(false);
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
      <div className="flex items-center justify-between border-b border-border bg-muted/40 px-3 py-2">
        <p className="truncate text-xs font-medium text-muted-foreground" title={asset.prompt ?? ""}>
          {asset.prompt || "Untitled"}
        </p>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="shrink-0 rounded-md p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
          title="Delete"
        >
          {deleting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Trash2 className="h-3.5 w-3.5" />}
        </button>
      </div>

      <div className="p-3">
        {asset.asset_type === "image" && asset.file_url ? (
          <img src={asset.file_url} alt={asset.prompt ?? ""} className="mb-2 max-h-48 w-full rounded-lg object-cover" />
        ) : null}
        {asset.asset_type === "video" && asset.file_url ? (
          <video src={asset.file_url} controls className="mb-2 max-h-48 w-full rounded-lg" />
        ) : null}
        {asset.asset_type === "audio" && asset.file_url ? (
          <audio src={asset.file_url} controls className="mb-2 w-full" />
        ) : null}
        {(asset.asset_type === "text" || asset.asset_type === "document" || asset.asset_type === "seo" || asset.asset_type === "script") && text ? (
          <p className="mb-2 max-h-32 overflow-hidden whitespace-pre-wrap text-xs text-foreground/80">
            {text.slice(0, 300)}
            {text.length > 300 ? "..." : ""}
          </p>
        ) : null}

        {asset.status === "failed" ? (
          <p className="mb-2 text-xs text-destructive">Generation failed.</p>
        ) : null}

        <div className="flex items-center justify-between">
          <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            {asset.asset_type}
          </span>
          <div className="flex items-center gap-1">
            {text ? (
              <button onClick={handleCopy} className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground" title="Copy">
                <Copy className="h-3.5 w-3.5" />
              </button>
            ) : null}
            {asset.file_url ? (
              <a href={asset.file_url} download className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground" title="Download">
                <Download className="h-3.5 w-3.5" />
              </a>
            ) : null}
          </div>
        </div>
        <p className="mt-2 text-[10px] text-muted-foreground">
          {new Date(asset.created_at).toLocaleDateString([], { day: "2-digit", month: "short", year: "numeric" })}
        </p>
      </div>
    </div>
  );
}

export default function AssetsLibraryPage() {
  const router = useRouter();
  const [assets, setAssets] = useState<LibraryAsset[]>([]);
  const [typeFilter, setTypeFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadFailed, setLoadFailed] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 24;

  async function loadAssets(reset: boolean) {
    setLoading(true);
    setLoadFailed(false);
    try {
      const nextOffset = reset ? 0 : offset;
      const { data } = await apiClient.get<LibraryAsset[]>("/api/v1/assets", {
        params: {
          asset_type: typeFilter || undefined,
          limit: LIMIT,
          offset: nextOffset,
        },
      });
      setAssets((prev) => (reset ? data : [...prev, ...data]));
      setOffset(nextOffset + data.length);
      setHasMore(data.length === LIMIT);
    } catch {
      setLoadFailed(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAssets(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [typeFilter]);

  function handleAssetDeleted(id: string) {
    setAssets((prev) => prev.filter((a) => a.id !== id));
  }

  return (
    <div className="mx-auto max-w-5xl p-6">
      <div className="mb-4 flex items-center gap-3">
        <button
          onClick={() => router.back()}
          title="Back"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Asset Library</h1>
          <p className="mt-1 text-sm text-muted-foreground">Everything you've generated - scripts, images, videos, audio, and more.</p>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-1.5">
        {TYPE_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setTypeFilter(f.value)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              typeFilter === f.value
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loadFailed ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center">
          <p className="mb-2 text-sm text-muted-foreground">Could not load your assets right now.</p>
          <button
            onClick={() => loadAssets(true)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-accent"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Try again
          </button>
        </div>
      ) : loading && assets.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
        </div>
      ) : assets.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
          <FileText className="mx-auto mb-2 h-6 w-6" />
          Nothing here yet. Generate something in Command Center and it'll show up here.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {assets.map((a) => (
              <AssetCard key={a.id} asset={a} onDelete={handleAssetDeleted} />
            ))}
          </div>
          {hasMore ? (
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => loadAssets(false)}
                disabled={loading}
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-accent disabled:opacity-50"
              >
                {loading ? "Loading..." : "Load more"}
              </button>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}

'@
[System.IO.File]::WriteAllText("C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\frontend\app\assets\page.tsx", $assetsContent, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Library page updated with delete button." -ForegroundColor Green
