"use client";

import { useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, FolderKanban } from "lucide-react";

import type { ProjectStatus } from "../types/project";
import { useProjectStore } from "../store/project.store";

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

interface ProjectDetailProps {
  id: string;
}

export default function ProjectDetail({ id }: ProjectDetailProps) {
  const project = useProjectStore((state) => state.currentProject);
  const isLoading = useProjectStore((state) => state.isLoadingCurrent);
  const error = useProjectStore((state) => state.error);
  const fetchProjectById = useProjectStore((state) => state.fetchProjectById);

  useEffect(() => {
    fetchProjectById(id);
  }, [id, fetchProjectById]);

  return (
    <main className="space-y-6">
      <Link
        href="/projects"
        className="flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Projects
      </Link>

      {isLoading && <p className="text-sm text-muted-foreground">Loading project...</p>}
      {error && !isLoading && <p className="text-sm text-red-500">{error}</p>}

      {!isLoading && !error && project && (
        <div className="rounded-2xl border border-border bg-card p-8 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent">
                <FolderKanban className="h-6 w-6 text-blue-600" />
              </div>
              <h1 className="text-2xl font-bold text-foreground">{project.name}</h1>
            </div>
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[project.status]}`}>
              {STATUS_LABELS[project.status]}
            </span>
          </div>

          <p className="mt-4 text-muted-foreground">
            {project.description || "No description provided."}
          </p>

          {project.brand_voice && (
            <div className="mt-6">
              <h2 className="text-sm font-semibold text-foreground">Brand Voice</h2>
              <p className="mt-1 text-sm text-muted-foreground">{project.brand_voice}</p>
            </div>
          )}

          <div className="mt-6 flex gap-6 text-xs text-muted-foreground">
            <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(project.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      )}
    </main>
  );
}
