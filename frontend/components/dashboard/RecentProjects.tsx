"use client";

import Link from "next/link";
import { useEffect } from "react";
import { FolderKanban, ArrowUpRight } from "lucide-react";

import { useProjectStore } from "@/features/projects/store/project.store";

export default function RecentProjects() {
  const projects = useProjectStore((state) => state.projects);
  const isLoading = useProjectStore((state) => state.isLoading ?? false);
  const fetchProjects = useProjectStore((state) => state.fetchProjects);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const recent = projects.slice(0, 5);

  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold tracking-tight text-foreground">Recent Projects</h2>
        <Link
          href="/projects"
          className="flex items-center gap-1 text-sm font-medium text-primary hover:underline"
        >
          View all
          <ArrowUpRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      <div className="mt-6 space-y-2">
        {isLoading && <p className="text-base text-muted-foreground">Loading projects...</p>}

        {!isLoading && recent.length === 0 && (
          <p className="text-base text-muted-foreground">No projects yet.</p>
        )}

        {recent.map((project) => (
          <div
            key={project.id}
            className="flex items-center gap-4 rounded-xl border border-transparent p-3 transition-colors hover:border-border hover:bg-accent"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent">
              <FolderKanban className="h-5 w-5 text-primary" />
            </div>
            <span className="text-base font-medium text-foreground">{project.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}