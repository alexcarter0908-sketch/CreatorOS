"use client";

import { useRouter } from "next/navigation";
import { FileText, Video, Image, Search } from "lucide-react";

const actions = [
  { title: "Generate Script", icon: FileText, prompt: "Write a script for my next video" },
  { title: "Video Prompt", icon: Video, prompt: "Generate a video for my brand" },
  { title: "Thumbnail Prompt", icon: Image, prompt: "Generate a thumbnail for my video" },
  { title: "SEO Generator", icon: Search, prompt: "Generate SEO tags for my video" },
];

export default function QuickActions() {
  const router = useRouter();

  function handleAction(prompt: string) {
    router.push(`/command-center?prefill=${encodeURIComponent(prompt)}`);
  }

  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-sm">
      <h2 className="font-console-display text-xl font-semibold tracking-tight text-foreground">Quick Actions</h2>

      <div className="mt-6 grid grid-cols-2 gap-4">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.title}
              onClick={() => handleAction(action.prompt)}
              className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-border p-6 transition-all duration-200 hover:border-primary/40 hover:bg-accent hover:shadow-sm"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent">
                <Icon className="h-6 w-6 text-primary" />
              </div>
              <span className="text-base font-medium text-foreground">{action.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}