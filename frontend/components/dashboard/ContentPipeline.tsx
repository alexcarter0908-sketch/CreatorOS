"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { listWorkflowsApi } from "@/features/workflows/services/workflow-api.service";
import type { WorkflowApi, WorkflowStepApi } from "@/features/workflows/types/workflow-api";

const STEP_LABELS: Record<string, string> = {
  text: "Script",
  script: "Script",
  document: "Script",
  seo: "SEO",
  image: "Thumbnail",
  video: "Video",
  audio: "Voice",
};

function stepLabel(step: WorkflowStepApi): string {
  return STEP_LABELS[step.asset_type] ?? step.asset_type;
}

function StepStatus({ status }: { status: WorkflowStepApi["status"] }) {
  if (status === "completed") {
    return <span className="text-xs font-console-mono text-emerald-400">â— Complete</span>;
  }
  if (status === "running") {
    return <span className="text-xs font-console-mono text-primary">â— Running</span>;
  }
  if (status === "failed") {
    return <span className="text-xs font-console-mono text-red-400">âœ• Failed</span>;
  }
  return <span className="text-xs font-console-mono text-muted-foreground">â—‹ Pending</span>;
}

export default function ContentPipeline() {
  const [workflow, setWorkflow] = useState<WorkflowApi | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    async function poll() {
      try {
        const workflows = await listWorkflowsApi();
        if (cancelled) return;

        const active = workflows.find(
          (w) => w.status === "running" || w.status === "completed_with_errors"
        );
        const current = active ?? workflows[0] ?? null;
        setWorkflow(current);
        setIsLoading(false);

        // Keep polling only while something is actively running, so the
        // step statuses update live without a manual page reload - and
        // stop automatically once it finishes (or this section unmounts).
        if (current?.status === "running" && !cancelled) {
          timeoutId = setTimeout(poll, 5000);
        }
      } catch {
        if (!cancelled) {
          setWorkflow(null);
          setIsLoading(false);
        }
      }
    }

    poll();

    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, []);

  const remaining = workflow?.steps.filter((s) => s.status !== "completed").length ?? 0;

  return (
    <div className="rounded-2xl border border-border bg-card shadow-sm">
      <div className="flex items-center justify-between p-7 pb-5">
        <h2 className="font-console-display text-xl font-semibold tracking-tight text-foreground">
          Content Pipeline
          {workflow && (
            <span className="ml-2 font-normal text-muted-foreground">â€” {workflow.name}</span>
          )}
        </h2>
        {workflow && remaining > 0 && (
          <span className="text-sm font-medium text-muted-foreground">
            {remaining} task{remaining === 1 ? "" : "s"} remaining
          </span>
        )}
      </div>

      {isLoading && (
        <p className="px-7 pb-7 text-sm text-muted-foreground">Loading pipeline...</p>
      )}

      {!isLoading && !workflow && (
        <div className="mx-7 mb-7 rounded-xl border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
          No active workflow yet.{" "}
          <Link href="/command-center" className="text-primary hover:underline">
            Start one in Command Center â†’
          </Link>
        </div>
      )}

      {!isLoading && workflow && (
        <div className="flex overflow-x-auto border-t border-border">
          {workflow.steps.map((step, idx) => (
            <div
              key={step.id}
              className="flex-1 shrink-0 basis-[170px] border-r border-dashed border-border/70 p-4 last:border-r-0"
            >
              <div className="mb-2 font-console-mono text-xs text-muted-foreground">
                {String(idx + 1).padStart(2, "0")}
              </div>
              <div className="mb-0.5 font-console-display text-sm font-semibold text-foreground">
                {stepLabel(step)}
              </div>
              <div className="mb-2 text-xs text-muted-foreground">
                {step.error_message ? "Error" : "AI"}
              </div>
              <StepStatus status={step.status} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}