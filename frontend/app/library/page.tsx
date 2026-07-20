"use client";

// Standalone gallery/history page for every generated asset (images, videos,
// scripts, SEO packages, audio) so users can browse & re-download past work
// without scrolling chat.
//
// Suggested route: frontend/app/library/page.tsx -> re-export this component.
//
// BACKEND TODO: assumes GET /api/v1/assets supports pagination + a type
// filter, returning objects shaped like the `Asset` type already used by
// asset.service.ts (features/assets/types/asset.ts). Adjust `fetchAssets`
// if your actual list endpoint differs (path, params, or response envelope).

import { useEffect, useState } from "react";
import Link from "next/link";
import { Download, FileText, Loader2, Search, Video, Image as ImageIcon, Music, FileCode2 } from "lucide-react";
import apiClient from "@/lib/api/client";
import type { Asset } from "@/features/assets/types/asset";

const PAGE_SIZE = 24;

const TYPE_FILTERS: { value: string; label: string }[] = [
  { value: "all", label: "All" },
  { value: "video", label: "Video" },
  { value: "image", label: "Image" },
  { value: "audio", label: "Audio" },
  { value: "script", label: "Script" },
  { value: "document", label: "Document" },
  { value: "seo", label: "SEO" },
];

const TYPE_ICON: Record<string, React.ReactNode> = {
  video: <Video className="h-4 w-4" />,
  image: <ImageIcon className="h-4 w-4" />,
  audio: <Music className="h-4 w-4" />,
  script: <FileCode2 className="h-4 w-4" />,
  document: <FileText className="h-4 w-4" />,
  seo: <FileCode2 className="h-4 w-4" />,
};

async function fetchAssets(params: { page: number; type?: string; q?: string }) {
  const { data } = await apiClient.get<{ items: Asset[]; total: number }>("/api/v1/assets", {
    params: {
      page: params.page,
      page_size: PAGE_SIZE,
      asset_type: params.type && params.type !== "all" ? params.type : undefined,
      q: params.q || undefined,
    },
  });
  return data;
}

function AssetThumb({ asset }: { asset: Asset }) {
  if (asset.asset_type === "image" && asset.file_url) {
    return <img src={asset.file_url} alt="" className="h-40 w-full rounded-lg object-cover" />;
  }
  if (asset.asset_type === "video" && asset.file_url) {
    return <video src={asset.file_url} className="h-40 w-full rounded-lg object-cover" muted />;
  }
  return (
    <div className="flex h-40 w-full items-center justify-center rounded-lg bg-muted text-muted-foreground">
      {TYPE_ICON[asset.asset_type] ?? <FileText className="h-6 w-6" />}
    </div>
  );
}

export default function AssetLibraryPage() {
  const [items, setItems] = useState<Asset[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [type, setType] = useState("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchAssets({ page, type, q: query })
      .then((data) => {
        if (cancelled) return;
        setItems(data.items);
        setTotal(data.total);
      })
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [page, type, query]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="mx-auto max-w-6xl p-6">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-xl font-semibold text-foreground">Asset library</h1>
        <div className="flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-1.5">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => {
              setPage(1);
              setQuery(e.target.value);
            }}
            placeholder="Search generated content..."
            className="w-56 bg-transparent text-sm outline-none"
          />
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {TYPE_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => {
              setPage(1);
              setType(f.value);
            }}
            className={`rounded-full border px-3 py-1 text-xs font-medium ${
              type === f.value
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border text-muted-foreground hover:bg-accent"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex h-40 items-center justify-center text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
          Nothing generated yet. Content you create in Command Center will show up here.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {items.map((asset) => (
            <div key={asset.id} className="overflow-hidden rounded-xl border border-border bg-card">
              <AssetThumb asset={asset} />
              <div className="flex items-center justify-between p-2.5">
                <div className="min-w-0">
                  <p className="truncate text-xs font-medium capitalize text-foreground">
                    {asset.asset_type || "Asset"}
                  </p>
                  <p className="text-[11px] text-muted-foreground">
                    {(asset as any).created_at
                      ? new Date((asset as any).created_at).toLocaleDateString([], { day: "2-digit", month: "short" })
                      : ""}
                  </p>
                </div>
                {asset.file_url ? (
                  <a
                    href={asset.file_url}
                    download
                    className="shrink-0 rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </a>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 ? (
        <div className="mt-6 flex items-center justify-center gap-2 text-sm">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="rounded-lg border border-border px-3 py-1.5 disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="rounded-lg border border-border px-3 py-1.5 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      ) : null}
    </div>
  );
}
