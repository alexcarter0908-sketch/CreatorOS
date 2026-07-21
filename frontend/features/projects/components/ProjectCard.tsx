"use client";

import { useState } from "react";
import Link from "next/link";
import { FolderKanban, Pencil, Trash2 } from "lucide-react";

import type { Project, ProjectStatus } from "../types/project";
import { Button } from "@/components/ui/button";
import EditProjectDialog from "./EditProjectDialog";
import DeleteProjectDialog from "./DeleteProjectDialog";

interface ProjectCardProps {
  project: Project;
}

const STATUS_STYLES: Record<ProjectStatus, string> = {
  active: "bg-green-100 text-green-700",
  draft: "bg-yellow-100 text-yellow-700",
  completed: "bg-blue-100 text-blue-700",
};

const STATUS_LABELS: Record<ProjectStatus, string> = {
  active: "Active",
  draft: "Draft",
  completed: "Completed",
};

export default function ProjectCard({ project }: ProjectCardProps) {
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  // Card actions sit inside a <Link>, so clicks on them must not trigger navigation.
  function stopNavigation(e: React.MouseEvent, action: () => void) {
    e.preventDefault();
    e.stopPropagation();
    action();
  }

  return (
    <div className="group relative rounded-2xl border border-border bg-card shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg">
      <Link href={`/projects/${project.id}`} className="block p-6">
        <div className="flex items-center justify-between">
          <FolderKanban className="h-8 w-8 text-blue-600" />
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[project.status]}`}>
            {STATUS_LABELS[project.status]}
          </span>
        </div>

        <h3 className="mt-5 text-xl font-semibold text-foreground">{project.name}</h3>
        <p className="mt-2 text-sm text-muted-foreground">{project.description}</p>
      </Link>

      <div className="flex items-center justify-end gap-1 border-t border-border/60 px-3 py-2 opacity-0 transition-opacity group-hover:opacity-100">
        <Button
          variant="outline"
          size="icon-sm"
          aria-label="Edit project"
          onClick={(e) => stopNavigation(e, () => setIsEditOpen(true))}
        >
          <Pencil className="h-3.5 w-3.5" />
        </Button>

        <Button
          variant="destructive"
          size="icon-sm"
          aria-label="Delete project"
          onClick={(e) => stopNavigation(e, () => setIsDeleteOpen(true))}
        >
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
      </div>

      <EditProjectDialog
        project={project}
        open={isEditOpen}
        onOpenChange={setIsEditOpen}
      />

      <DeleteProjectDialog
        project={project}
        open={isDeleteOpen}
        onOpenChange={setIsDeleteOpen}
      />
    </div>
  );
}