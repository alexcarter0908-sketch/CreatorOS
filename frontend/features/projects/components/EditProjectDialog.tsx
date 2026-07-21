"use client";

import { useEffect, useState } from "react";
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
  const updateProject = useProjectStore((state) => state.updateProject);
  const isUpdating = useProjectStore((state) => state.isUpdating);

  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description ?? "");
  const [brandVoice, setBrandVoice] = useState(project.brand_voice ?? "");
  const [status, setStatus] = useState<ProjectStatus>(project.status);

  // Re-sync form fields whenever a different project is opened for editing.
  useEffect(() => {
    if (open) {
      setName(project.name);
      setDescription(project.description ?? "");
      setBrandVoice(project.brand_voice ?? "");
      setStatus(project.status);
    }
  }, [open, project]);

  async function handleSave() {
    if (!name.trim()) {
      toast.error("Project name is required.");
      return;
    }

    try {
      await updateProject(project.id, {
        name: name.trim(),
        description: description.trim(),
        brand_voice: brandVoice.trim(),
        status,
      });

      toast.success("Project updated.");
      onOpenChange(false);
    } catch {
      toast.error("Failed to update project.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit Project</DialogTitle>
        </DialogHeader>

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
            <Label htmlFor="edit-project-status">Status</Label>
            <select
              id="edit-project-status"
              value={status}
              onChange={(e) => setStatus(e.target.value as ProjectStatus)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
            >
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <Button className="w-full" onClick={handleSave} disabled={isUpdating}>
            {isUpdating ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}