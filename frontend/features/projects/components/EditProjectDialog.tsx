"use client";

import { useState } from "react";
import { toast } from "sonner";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

import { useProjectStore } from "../store/project.store";
import type { Project, ProjectStatus } from "../types/project";

interface Props {
  project: Project;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const STATUS_OPTIONS: { value: ProjectStatus; label: string }[] = [
  { value: "draft", label: "Draft" },
  { value: "active", label: "Active" },
  { value: "completed", label: "Completed" },
];

export default function EditProjectDialog({ project, open, onOpenChange }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit Project</DialogTitle>
        </DialogHeader>

        {open && <EditProjectForm project={project} onOpenChange={onOpenChange} />}
      </DialogContent>
    </Dialog>
  );
}

function EditProjectForm({
  project,
  onOpenChange,
}: {
  project: Project;
  onOpenChange: (open: boolean) => void;
}) {
  const editProject = useProjectStore((state) => state.editProject);
  const isUpdating = useProjectStore((state) => state.isSaving);

  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description ?? "");
  const [brandVoice, setBrandVoice] = useState(project.brand_voice ?? "");
  const [status, setStatus] = useState<ProjectStatus>(project.status);
  const [statusAuto, setStatusAuto] = useState(project.status_auto);

  async function handleSave() {
    if (!name.trim()) {
      toast.error("Project name is required.");
      return;
    }

    try {
      await editProject(project.id, {
        name: name.trim(),
        description: description.trim(),
        brand_voice: brandVoice.trim(),
        // If auto mode is on, don't force a status - let the system keep
        // deciding. If the user turned auto off, their picked status wins.
        ...(statusAuto ? { status_auto: true } : { status, status_auto: false }),
      });

      toast.success("Project updated.");
      onOpenChange(false);
    } catch {
      toast.error("Failed to update project.");
    }
  }

  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <Label htmlFor="edit-project-name">Project Name</Label>
        <Input
          id="edit-project-name"
          placeholder="Project Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="edit-project-description">Description</Label>
        <Textarea
          id="edit-project-description"
          placeholder="Project Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="edit-project-brand-voice">Brand Voice</Label>
        <Textarea
          id="edit-project-brand-voice"
          placeholder="Brand Voice (optional) - e.g. casual and friendly, always use emojis, no formal language"
          value={brandVoice}
          onChange={(e) => setBrandVoice(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="edit-project-status">Status</Label>
          <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <input
              id="edit-project-status-auto"
              type="checkbox"
              checked={statusAuto}
              onChange={(e) => setStatusAuto(e.target.checked)}
              className="h-3.5 w-3.5"
            />
            Auto (recommended)
          </label>
        </div>
        <select
          id="edit-project-status"
          value={status}
          disabled={statusAuto}
          onChange={(e) => setStatus(e.target.value as ProjectStatus)}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
        >
          {STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {statusAuto && (
          <p className="text-xs text-muted-foreground">
            System will move this from Draft to Active once you generate content in it.
            Uncheck to set the status yourself.
          </p>
        )}
      </div>

      <Button className="w-full" onClick={handleSave} disabled={isUpdating}>
        {isUpdating ? "Saving..." : "Save Changes"}
      </Button>
    </div>
  );
}
