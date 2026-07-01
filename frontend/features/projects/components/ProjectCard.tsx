import { FolderKanban } from "lucide-react";

interface ProjectCardProps {
  title: string;
  description: string;
}

export default function ProjectCard({
  title,
  description,
}: ProjectCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg">
      <div className="flex items-center justify-between">
        <FolderKanban className="h-8 w-8 text-blue-600" />

        <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
          Active
        </span>
      </div>

      <h3 className="mt-5 text-xl font-semibold text-slate-900">
        {title}
      </h3>

      <p className="mt-2 text-sm text-slate-500">
        {description}
      </p>
    </div>
  );
}