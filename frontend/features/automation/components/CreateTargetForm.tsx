"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

import { useAutoTargetStore } from "../store/target.store";
import type { AutoTargetAssetType } from "../types/target";

const ASSET_TYPES: { value: AutoTargetAssetType; label: string }[] = [
  { value: "text", label: "Script / Text" },
  { value: "image", label: "Image / Thumbnail" },
  { value: "video", label: "Video" },
  { value: "audio", label: "Audio / Voice" },
];

const FREQUENCIES = [
  { value: 24, label: "Every day" },
  { value: 12, label: "Every 12 hours" },
  { value: 6, label: "Every 6 hours" },
  { value: 168, label: "Every week" },
];

export default function CreateTargetForm() {
  const addTarget = useAutoTargetStore((state) => state.addTarget);

  const [assetType, setAssetType] = useState<AutoTargetAssetType>("text");
  const [prompt, setPrompt] = useState("");
  const [frequencyHours, setFrequencyHours] = useState(24);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsSubmitting(true);
    try {
      await addTarget({
        asset_type: assetType,
        prompt: prompt.trim(),
        frequency_hours: frequencyHours,
      });
      toast.success("Automation target created.");
      setPrompt("");
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
          CreatorOS will automatically generate this on a recurring schedule.
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
        <Label>Frequency</Label>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {FREQUENCIES.map((freq) => (
            <button
              type="button"
              key={freq.value}
              onClick={() => setFrequencyHours(freq.value)}
              className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                frequencyHours === freq.value
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-border text-muted-foreground hover:border-slate-300"
              }`}
            >
              {freq.label}
            </button>
          ))}
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Activate Automation"}
      </Button>
    </form>
  );
}
