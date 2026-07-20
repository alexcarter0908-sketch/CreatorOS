"use client";

import { useEffect } from "react";
import { Trash2, Zap, ZapOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAutoTargetStore } from "../store/target.store";

const ASSET_TYPE_LABELS: Record<string, string> = {
  text: "Script / Text",
  image: "Image / Thumbnail",
  video: "Video",
  audio: "Audio / Voice",
};

function formatFrequency(hours: number): string {
  if (hours >= 168) return "Weekly";
  if (hours >= 24) return "Daily";
  return `Every ${hours}h`;
}

export default function TargetList() {
  const targets = useAutoTargetStore((state) => state.targets);
  const isLoading = useAutoTargetStore((state) => state.isLoading);
  const error = useAutoTargetStore((state) => state.error);
  const fetchTargets = useAutoTargetStore((state) => state.fetchTargets);
  const removeTarget = useAutoTargetStore((state) => state.removeTarget);

  useEffect(() => {
    fetchTargets();
  }, [fetchTargets]);

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading automation targets...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-500">{error}</p>;
  }

  if (targets.length === 0) {
    return (
      <div className="rounded-xl border border-dashed p-10 text-center text-sm text-muted-foreground">
        No automation targets yet. Create one to let CreatorOS work for you.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {targets.map((target) => (
        <div
          key={target.id}
          className="flex items-start justify-between gap-4 rounded-xl border bg-card p-5 shadow-sm"
        >
          <div className="flex items-start gap-3">
            <div
              className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                target.is_active
                  ? "bg-green-100 text-green-600"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {target.is_active ? (
                <Zap className="h-4 w-4" />
              ) : (
                <ZapOff className="h-4 w-4" />
              )}
            </div>

            <div>
              <p className="text-sm font-medium text-foreground">{target.prompt}</p>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                <span className="rounded-full bg-muted px-2 py-0.5">
                  {ASSET_TYPE_LABELS[target.asset_type] ?? target.asset_type}
                </span>
                <span className="rounded-full bg-muted px-2 py-0.5">
                  {formatFrequency(target.frequency_hours)}
                </span>
                <span>
                  {target.last_run_at
                    ? `Last run: ${new Date(target.last_run_at).toLocaleString()}`
                    : "Not run yet"}
                </span>
              </div>
            </div>
          </div>

          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => removeTarget(target.id)}
            className="text-red-500 hover:bg-red-50 hover:text-red-600"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  );
}
