import { FileText, Video, Image, Search } from "lucide-react";

const actions = [
  {
    title: "Generate Script",
    icon: FileText,
  },
  {
    title: "Video Prompt",
    icon: Video,
  },
  {
    title: "Thumbnail Prompt",
    icon: Image,
  },
  {
    title: "SEO Generator",
    icon: Search,
  },
];

export default function QuickActions() {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">
        Quick Actions
      </h2>

      <div className="mt-6 grid grid-cols-2 gap-4">
        {actions.map((action) => {
          const Icon = action.icon;

          return (
            <button
              key={action.title}
              className="flex flex-col items-center justify-center rounded-xl border p-5 transition-all hover:border-blue-500 hover:bg-blue-50"
            >
              <Icon className="mb-3 h-8 w-8 text-blue-600" />

              <span className="text-sm font-medium">
                {action.title}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}