"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Youtube, Instagram, Facebook, MessageCircle, Twitter, ExternalLink, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "../../lib/api/client";
import BrandWatermark from "@/components/common/BrandWatermark";
import "@/styles/console-theme.css";

const COMING_SOON_PLATFORMS = [
  { name: "Instagram", icon: Instagram, color: "text-pink-600", bg: "bg-pink-50" },
  { name: "TikTok", icon: MessageCircle, color: "text-slate-900", bg: "bg-slate-100" },
  { name: "Facebook", icon: Facebook, color: "text-blue-600", bg: "bg-blue-50" },
  { name: "X (Twitter)", icon: Twitter, color: "text-slate-900", bg: "bg-slate-100" },
  { name: "WhatsApp", icon: MessageCircle, color: "text-green-600", bg: "bg-green-50" },
];

interface ConnectedAccount {
  id: string;
  platform: string;
  account_label: string | null;
  external_account_id: string | null;
}

export default function ConnectionsPage() {
  const router = useRouter();
  const [connectingYouTube, setConnectingYouTube] = useState(false);
  const [youtubeAccounts, setYoutubeAccounts] = useState<ConnectedAccount[]>([]);
  const [loadingAccounts, setLoadingAccounts] = useState(true);

  useEffect(() => {
    apiClient<{ accounts: ConnectedAccount[] }>("/api/v1/publish/accounts")
      .then((res) => {
        setYoutubeAccounts((res.data?.accounts || []).filter((a) => a.platform === "youtube"));
      })
      .catch(() => {})
      .finally(() => setLoadingAccounts(false));
  }, []);

  async function connectYouTube() {
    setConnectingYouTube(true);
    try {
      const response = await apiClient<{ authorization_url: string }>(
        "/api/v1/publish/youtube/connect"
      );
      const url = response.data?.authorization_url;
      if (url) window.open(url, "_blank");
    } catch {
      alert("Could not start YouTube connection. Is the backend running?");
    } finally {
      setConnectingYouTube(false);
    }
  }

  return (
    <div className="console-theme relative isolate min-h-screen overflow-hidden">
      <BrandWatermark />
      <div className="relative z-10 mx-auto max-w-2xl p-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          title="Back"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Connections</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Connect your accounts so Synapse-X-CreatorOS can publish content on your behalf.
          </p>
        </div>
      </div>
      <div className="mt-6 space-y-3">
        <div className="flex items-center justify-between rounded-xl border border-border bg-card p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50 text-red-600">
              <Youtube className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium text-foreground">YouTube</p>
              <p className="text-xs text-muted-foreground">Upload videos to your channel automatically.</p>
            </div>
          </div>
          <Button size="sm" onClick={connectYouTube} disabled={connectingYouTube} className="gap-1.5">
            {connectingYouTube ? "Opening..." : youtubeAccounts.length > 0 ? "Add another channel" : "Connect"}
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
        {!loadingAccounts && youtubeAccounts.length > 0 ? (
          <div className="ml-13 space-y-1.5 pl-[52px]">
            {youtubeAccounts.map((acc) => (
              <div
                key={acc.id}
                className="flex items-center gap-2 rounded-lg border border-border bg-muted/40 px-3 py-1.5 text-xs text-muted-foreground"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                {acc.account_label || "Connected channel"}
              </div>
            ))}
          </div>
        ) : null}

        {COMING_SOON_PLATFORMS.map((platform) => {
          const Icon = platform.icon;
          return (
            <div
              key={platform.name}
              className="flex items-center justify-between rounded-xl border border-border bg-card p-4 opacity-60"
            >
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${platform.bg} ${platform.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <p className="font-medium text-foreground">{platform.name}</p>
              </div>
              <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                Coming soon
              </span>
            </div>
          );
        })}
      </div>
    </div>
    </div>
  );
}


