"use client";

import CreateProjectButton from "./CreateProjectButton";
import ProjectCard from "./ProjectCard";
import { useProjectStore } from "../store/project.store";

export default function ProjectsPage() {
  const projects = useProjectStore((state) => state.projects);

  return (
    <main className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Projects
          </h1>

          <p className="mt-2 text-slate-500">
            Manage all your AI content projects.
          </p>
        </div>

        <CreateProjectButton />
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            title={project.name}
            description={project.description}
            status={project.status}
          />
        ))}
      </div>
    </main>
  );
}