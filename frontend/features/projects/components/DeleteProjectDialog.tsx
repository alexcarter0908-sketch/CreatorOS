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

import { useProjectStore } from "../store/project.store";
import type { Project } from "../types/project";

interface Props {
  project: Project;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  // Called after the project has been deleted successfully.
  // Useful for e.g. redirecting away from a project detail page.
  onDeleted?: () => void;
}

export default function DeleteProjectDialog({
  project,
  open,
  onOpenChange,
  onDeleted,
}: Props) {
  const removeProject = useProjectStore((state) => state.removeProject);
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleDelete() {
    setIsDeleting(true);

    try {
      await removeProject(project.id);
      toast.success("Project deleted.");
      onOpenChange(false);
      onDeleted?.();
    } catch {
      toast.error("Failed to delete project.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Delete Project</DialogTitle>
        </DialogHeader>

        <p className="text-sm text-muted-foreground">
          Are you sure you want to delete <span className="font-semibold text-foreground">{project.name}</span>?
          This action cannot be undone.
        </p>

        <div className="flex justify-end gap-3 pt-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}