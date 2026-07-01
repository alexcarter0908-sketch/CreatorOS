import { FolderKanban } from "lucide-react";

interface ProjectCardProps {
  title: string;
  description: string;
  status: "Active" | "Draft" | "Completed";
}

export default function ProjectCard({
  title,
  description,
  status,
}: ProjectCardProps) {
  const statusStyles = {
    Active: "bg-green-100 text-green-700",
    Draft: "bg-yellow-100 text-yellow-700",
    Completed: "bg-blue-100 text-blue-700",
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg">
      <div className="flex items-center justify-between">
        <FolderKanban className="h-8 w-8 text-blue-600" />

        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[status]}`}
        >
          {status}
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