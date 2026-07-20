"use client";

import { useEffect } from "react";

import CreateProjectButton from "./CreateProjectButton";
import ProjectCard from "./ProjectCard";
import { useProjectStore } from "../store/project.store";

export default function ProjectsPage() {
  const projects = useProjectStore((state) => state.projects);
  const isLoading = useProjectStore((state) => state.isLoading);
  const error = useProjectStore((state) => state.error);
  const fetchProjects = useProjectStore((state) => state.fetchProjects);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return (
    <main className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Projects</h1>
          <p className="mt-2 text-muted-foreground">Manage all your AI content projects.</p>
        </div>

        <CreateProjectButton />
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading projects...</p>}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {!isLoading && !error && projects.length === 0 && (
        <div className="rounded-xl border border-dashed p-10 text-center text-sm text-muted-foreground">
          No projects yet. Create your first one.
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            title={project.name}
            description={project.description ?? ""}
            status={project.status}
          />
        ))}
      </div>
    </main>
  );
}
