"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { listAssets } from "@/features/assets/services/asset.service";
import type { Asset } from "@/features/assets/types/asset";

const TYPE_ICON: Record<string, string> = {
  video: "🎬",
  image: "🖼️",
  audio: "🎙️",
  text: "📝",
  script: "📝",
  document: "📄",
  seo: "🔍",
};

const STATUS_VERB: Record<string, string> = {
  completed: "generated",
  failed: "failed",
  pending: "queued",
};

function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d`;
}

function describeAsset(asset: Asset): string {
  const icon = TYPE_ICON[asset.asset_type] ?? "✨";
  const verb = STATUS_VERB[asset.status] ?? asset.status;
  const label = asset.asset_type === "text" ? "Script" : asset.asset_type;
  const title = asset.prompt ? `— ${asset.prompt.slice(0, 40)}${asset.prompt.length > 40 ? "…" : ""}` : "";
  return `${icon} ${label.charAt(0).toUpperCase() + label.slice(1)} ${verb} ${title}`;
}

export default function RecentActivity() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    listAssets()
      .then((data) => {
        if (!cancelled) setAssets(data.slice(0, 5));
      })
      .catch(() => {
        if (!cancelled) setAssets([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold tracking-tight text-foreground">Recent Activity</h2>
        <Link href="/assets" className="text-sm font-medium text-primary hover:underline">
          View all
        </Link>
      </div>

      <div className="mt-6">
        {isLoading && <p className="text-sm text-muted-foreground">Loading activity...</p>}

        {!isLoading && assets.length === 0 && (
          <p className="text-sm text-muted-foreground">No activity yet.</p>
        )}

        {!isLoading &&
          assets.map((asset) => (
            <div
              key={asset.id}
              className="flex items-center gap-3 border-b border-border/60 py-3 text-sm text-foreground last:border-b-0"
            >
              <span className="flex-1 truncate">{describeAsset(asset)}</span>
              <span className="shrink-0 font-console-mono text-xs text-muted-foreground">
                {relativeTime(asset.created_at)}
              </span>
            </div>
          ))}
      </div>
    </div>
  );
}
