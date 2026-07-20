"use client";

// Small badge row showing which generation providers are currently
// available, e.g. "Video: Runway ✅  PixVerse ⚠️". Drop this above
// CommandInput (or inside its header) so users know what's available
// before they generate.
//
// BACKEND TODO: this assumes a GET /api/v1/providers/status endpoint that
// returns something like:
//   { providers: [{ asset_type: "video", name: "Runway", status: "up" }, ...] }
// If your backend exposes this differently (e.g. per-workflow-step health,
// or nested under /api/v1/settings), adjust `fetchProviderStatus` below -
// the rest of the component only depends on the `ProviderStatus[]` shape.

import { useEffect, useState } from "react";
import { CheckCircle2, AlertTriangle, XCircle, RefreshCw } from "lucide-react";
import apiClient from "@/lib/api/client";

type ProviderHealth = "up" | "degraded" | "down";

interface ProviderStatus {
  asset_type: string; // "video" | "image" | "audio" | "text" | "seo" ...
  name: string; // e.g. "Runway", "PixVerse", "ElevenLabs"
  status: ProviderHealth;
}

const ASSET_TYPE_LABELS: Record<string, string> = {
  video: "Video",
  image: "Image",
  audio: "Audio",
  text: "Script",
  seo: "SEO",
};

const STATUS_ICON: Record<ProviderHealth, React.ReactNode> = {
  up: <CheckCircle2 className="h-3 w-3 text-emerald-500" />,
  degraded: <AlertTriangle className="h-3 w-3 text-amber-500" />,
  down: <XCircle className="h-3 w-3 text-destructive" />,
};

async function fetchProviderStatus(): Promise<ProviderStatus[]> {
  const { data } = await apiClient.get<{ providers: ProviderStatus[] }>("/api/v1/providers/status");
  return data.providers ?? [];
}

export default function ProviderStatusBadge() {
  const [providers, setProviders] = useState<ProviderStatus[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [errored, setErrored] = useState(false);

  async function load() {
    setLoading(true);
    setErrored(false);
    try {
      const result = await fetchProviderStatus();
      setProviders(result);
    } catch {
      setErrored(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 60_000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  // Group by asset type, keep only the first provider per type for a compact
  // row; if you support multiple providers per asset type simultaneously,
  // remove the `.slice(0, 1)` to show all of them.
  const grouped = (providers ?? []).reduce<Record<string, ProviderStatus[]>>((acc, p) => {
    acc[p.asset_type] = acc[p.asset_type] ? [...acc[p.asset_type], p] : [p];
    return acc;
  }, {});

  if (errored) {
    return (
      <button
        onClick={load}
        className="flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground hover:bg-accent"
      >
        <RefreshCw className="h-3 w-3" />
        Provider status unavailable
      </button>
    );
  }

  if (loading && !providers) {
    return <div className="h-6 w-40 animate-pulse rounded-full bg-muted" />;
  }

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {Object.entries(grouped).map(([assetType, list]) => (
        <div
          key={assetType}
          className="flex items-center gap-1 rounded-full border border-border bg-background px-2.5 py-1 text-xs"
          title={list.map((p) => `${p.name}: ${p.status}`).join(", ")}
        >
          <span className="font-medium text-foreground">{ASSET_TYPE_LABELS[assetType] ?? assetType}:</span>
          {list.map((p) => (
            <span key={p.name} className="flex items-center gap-0.5 text-muted-foreground">
              {STATUS_ICON[p.status]}
              {p.name}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}
