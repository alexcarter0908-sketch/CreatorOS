"use client";

import { useEffect, useState } from "react";
import { Youtube, ChevronDown, Loader2, Check } from "lucide-react";
import apiClient from "@/lib/api/client";

interface ConnectedAccount {
  id: string;
  platform: string;
  account_label: string | null;
  external_account_id: string | null;
}

interface PublishToYouTubeButtonProps {
  assetId: string;
  defaultTitle?: string;
  defaultDescription?: string;
}

export default function PublishToYouTubeButton({
  assetId,
  defaultTitle = "",
  defaultDescription = "",
}: PublishToYouTubeButtonProps) {
  const [open, setOpen] = useState(false);
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [publishing, setPublishing] = useState(false);
  const [published, setPublished] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || accounts.length > 0) return;
    setLoadingAccounts(true);
    apiClient
      .get<{ accounts: ConnectedAccount[] }>("/api/v1/publish/accounts")
      .then(({ data }) => {
        const yt = (data?.accounts || []).filter((a) => a.platform === "youtube");
        setAccounts(yt);
        if (yt.length > 0) setSelectedAccountId(yt[0].id);
      })
      .catch(() => setError("Could not load connected channels."))
      .finally(() => setLoadingAccounts(false));
  }, [open, accounts.length]);

  async function handlePublish() {
    if (!selectedAccountId) return;
    setPublishing(true);
    setError(null);
    try {
      await apiClient.post(`/api/v1/publish/youtube/upload/${assetId}`, {
        title: defaultTitle || "CreatorOS video",
        description: defaultDescription,
        tags: [],
        privacy_status: "private",
        account_id: selectedAccountId,
      });
      setPublished(true);
      setOpen(false);
    } catch (err) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Could not publish to YouTube.";
      setError(message);
    } finally {
      setPublishing(false);
    }
  }

  if (published) {
    return (
      <span className="flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1.5 text-xs font-medium text-emerald-600">
        <Check className="h-3.5 w-3.5" />
        Published
      </span>
    );
  }

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 rounded-lg border border-border bg-background px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
      >
        <Youtube className="h-3.5 w-3.5" />
        Publish to YouTube
        <ChevronDown className={`h-3 w-3 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open ? (
        <div className="absolute left-0 top-full z-20 mt-1 w-64 rounded-xl border border-border bg-popover p-2 shadow-xl">
          {loadingAccounts ? (
            <div className="flex items-center gap-2 px-2 py-2 text-xs text-muted-foreground">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Loading channels...
            </div>
          ) : accounts.length === 0 ? (
            <div className="px-2 py-2 text-xs text-muted-foreground">
              No YouTube channel connected.{" "}
              <a href="/connections" className="text-primary hover:underline">
                Connect one
              </a>
            </div>
          ) : (
            <>
              <div className="mb-1.5 px-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
                Choose a channel
              </div>
              <div className="max-h-40 space-y-0.5 overflow-y-auto">
                {accounts.map((acc) => (
                  <button
                    key={acc.id}
                    onClick={() => setSelectedAccountId(acc.id)}
                    className={`flex w-full items-center justify-between rounded-lg px-2 py-1.5 text-left text-xs hover:bg-accent ${
                      selectedAccountId === acc.id ? "bg-accent font-medium" : ""
                    }`}
                  >
                    {acc.account_label || "Connected channel"}
                    {selectedAccountId === acc.id ? <Check className="h-3.5 w-3.5" /> : null}
                  </button>
                ))}
              </div>
              <button
                onClick={handlePublish}
                disabled={publishing || !selectedAccountId}
                className="mt-2 flex w-full items-center justify-center gap-1.5 rounded-lg bg-primary px-2.5 py-1.5 text-xs font-medium text-primary-foreground hover:opacity-90 disabled:opacity-60"
              >
                {publishing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Youtube className="h-3.5 w-3.5" />}
                {publishing ? "Publishing..." : "Publish"}
              </button>
            </>
          )}
          {error ? <p className="mt-1.5 px-1 text-[11px] text-destructive">{error}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
