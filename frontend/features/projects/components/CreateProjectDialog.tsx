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

import { useProjectStore } from "../store/project.store";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function CreateProjectDialog({ open, onOpenChange }: Props) {
  const addProject = useProjectStore((state) => state.addProject);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [brandVoice, setBrandVoice] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleCreate() {
    if (!name.trim()) return;

    setIsSubmitting(true);

    try {
      await addProject({
        name: name.trim(),
        description: description.trim() || undefined,
        brand_voice: brandVoice.trim() || undefined,
      });

      toast.success("Project created.");
      setName("");
      setDescription("");
      setBrandVoice("");
      onOpenChange(false);
    } catch {
      toast.error("Failed to create project.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create Project</DialogTitle>
        </DialogHeader>

        <div className="space-y-5">
          <Input
            placeholder="Project Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <Textarea
            placeholder="Project Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <Textarea
            placeholder="Brand Voice (optional) - e.g. casual and friendly, always use emojis, no formal language"
            value={brandVoice}
            onChange={(e) => setBrandVoice(e.target.value)}
          />

          <Button className="w-full" onClick={handleCreate} disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create Project"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}