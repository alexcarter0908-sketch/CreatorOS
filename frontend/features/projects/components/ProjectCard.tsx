import Link from "next/link";
import { FolderKanban } from "lucide-react";
import type { ProjectStatus } from "../types/project";

interface ProjectCardProps {
  id: string;
  title: string;
  description: string;
  status: ProjectStatus;
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

export default function ProjectCard({ id, title, description, status }: ProjectCardProps) {
  return (
    <Link
      href={`/projects/${id}`}
      className="block rounded-2xl border border-border bg-card p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg"
    >
      <div className="flex items-center justify-between">
        <FolderKanban className="h-8 w-8 text-blue-600" />
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[status]}`}>
          {STATUS_LABELS[status]}
        </span>
      </div>

      <h3 className="mt-5 text-xl font-semibold text-foreground">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </Link>
  );
}
