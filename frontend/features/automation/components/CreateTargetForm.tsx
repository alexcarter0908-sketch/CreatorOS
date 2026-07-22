"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";

import { useAutoTargetStore } from "../store/target.store";
import type { AutoTargetAssetType } from "../types/target";
import { useProjectStore } from "@/features/projects/store/project.store";

const ASSET_TYPES: { value: AutoTargetAssetType; label: string }[] = [
  { value: "text", label: "Script / Text" },
  { value: "image", label: "Image / Thumbnail" },
  { value: "video", label: "Video" },
  { value: "audio", label: "Audio / Voice" },
];

// Only "video" runs the full script -> thumbnail -> video -> SEO pipeline
// and can be auto-published (to YouTube today). Other asset types generate
// a single asset and are never published automatically.
const PUBLISHABLE_ASSET_TYPE: AutoTargetAssetType = "video";

const INTERVAL_PRESETS = [
  { value: 1, label: "Every day" },
  { value: 3, label: "Every 3 days" },
  { value: 7, label: "Weekly" },
];

function toTimeInputValue(hour: number, minute: number): string {
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

export default function CreateTargetForm() {
  const addTarget = useAutoTargetStore((state) => state.addTarget);

  const projects = useProjectStore((state) => state.projects);
  const fetchProjects = useProjectStore((state) => state.fetchProjects);

  const [assetType, setAssetType] = useState<AutoTargetAssetType>("text");
  const [prompt, setPrompt] = useState("");
  const [projectId, setProjectId] = useState<string>("");

  const [intervalDays, setIntervalDays] = useState(1);
  const [customInterval, setCustomInterval] = useState(false);
  const [timeOfDay, setTimeOfDay] = useState(toTimeInputValue(9, 0));

  const [autoPublish, setAutoPublish] = useState(true);
  const [tags, setTags] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!prompt.trim()) return;

    const [hourStr, minuteStr] = timeOfDay.split(":");

    setIsSubmitting(true);
    try {
      await addTarget({
        asset_type: assetType,
        prompt: prompt.trim(),
        project_id: projectId || undefined,
        interval_days: Math.max(1, intervalDays),
        run_at_hour: Number(hourStr) || 0,
        run_at_minute: Number(minuteStr) || 0,
        auto_publish: assetType === PUBLISHABLE_ASSET_TYPE ? autoPublish : false,
        platforms: assetType === PUBLISHABLE_ASSET_TYPE && autoPublish ? ["youtube"] : [],
        tags: tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      });
      toast.success("Automation target created.");
      setPrompt("");
      setTags("");
    } catch {
      toast.error("Failed to create target.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-2xl border bg-card p-6 shadow-sm">
      <div>
        <h2 className="text-xl font-semibold text-foreground">New Automation Target</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Synapse-X-CreatorOS will automatically generate this on a recurring schedule.
        </p>
      </div>

      <div className="space-y-2">
        <Label>Asset Type</Label>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {ASSET_TYPES.map((type) => (
            <button
              type="button"
              key={type.value}
              onClick={() => setAssetType(type.value)}
              className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                assetType === type.value
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-border text-muted-foreground hover:border-slate-300"
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="target-prompt">Prompt</Label>
        <Textarea
          id="target-prompt"
          placeholder="e.g. Generate a motivational quote graphic for creators"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="target-project">Project (optional)</Label>
        <select
          id="target-project"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
        >
          <option value="">No project</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <Label>Runs every</Label>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {INTERVAL_PRESETS.map((preset) => (
            <button
              type="button"
              key={preset.value}
              onClick={() => {
                setIntervalDays(preset.value);
                setCustomInterval(false);
              }}
              className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                !customInterval && intervalDays === preset.value
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-border text-muted-foreground hover:border-slate-300"
              }`}
            >
              {preset.label}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setCustomInterval(true)}
            className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
              customInterval
                ? "border-blue-600 bg-blue-50 text-blue-700"
                : "border-border text-muted-foreground hover:border-slate-300"
            }`}
          >
            Custom
          </button>
        </div>

        {customInterval && (
          <div className="flex items-center gap-2 pt-1">
            <span className="text-sm text-muted-foreground">Every</span>
            <Input
              type="number"
              min={1}
              value={intervalDays}
              onChange={(e) => setIntervalDays(Math.max(1, Number(e.target.value) || 1))}
              className="w-20"
            />
            <span className="text-sm text-muted-foreground">day(s)</span>
          </div>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="target-time">At (time of day)</Label>
        <Input
          id="target-time"
          type="time"
          value={timeOfDay}
          onChange={(e) => setTimeOfDay(e.target.value)}
          className="w-40"
        />
      </div>

      {assetType === PUBLISHABLE_ASSET_TYPE && (
        <div className="space-y-3 rounded-lg border border-dashed border-border p-4">
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            <input
              type="checkbox"
              checked={autoPublish}
              onChange={(e) => setAutoPublish(e.target.checked)}
              className="h-4 w-4 rounded border-input"
            />
            Auto-publish to YouTube when ready
          </label>
          <p className="text-xs text-muted-foreground">
            Requires a connected YouTube account (Connections page). Other platforms are coming soon.
          </p>

          {autoPublish && (
            <div className="space-y-2">
              <Label htmlFor="target-tags">Tags (comma separated, optional)</Label>
              <Input
                id="target-tags"
                placeholder="e.g. shorts, motivation, creator"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
              />
            </div>
          )}
        </div>
      )}

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Activate Automation"}
      </Button>
    </form>
  );
}