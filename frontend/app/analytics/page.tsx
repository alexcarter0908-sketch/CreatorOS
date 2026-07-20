"use client";

import MainLayout from "@/components/layout/MainLayout";
import { useDashboardStats } from "@/lib/hooks/useDashboardStats";

const BAR_COLORS: Record<string, string> = {
  Scripts: "bg-green-500",
  Videos: "bg-purple-500",
  Images: "bg-blue-500",
  Audio: "bg-orange-500",
};

export default function AnalyticsPage() {
  const stats = useDashboardStats();

  const breakdown = [
    { label: "Scripts", value: stats.scripts },
    { label: "Videos", value: stats.videos },
    { label: "Images", value: stats.images },
    { label: "Audio", value: stats.audio },
  ];

  const total = breakdown.reduce((sum, item) => sum + item.value, 0) || 1;

  return (
    <MainLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
        <p className="mt-2 text-muted-foreground">
          A breakdown of everything CreatorOS has generated for you.
        </p>
      </div>

      <div className="rounded-2xl border bg-card p-6 shadow-sm">
        <h2 className="mb-6 text-lg font-semibold text-foreground">Content Breakdown</h2>

        <div className="space-y-5">
          {breakdown.map((item) => {
            const percent = Math.round((item.value / total) * 100);

            return (
              <div key={item.label}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span className="font-medium text-foreground">{item.label}</span>
                  <span className="text-muted-foreground">{item.value}</span>
                </div>

                <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className={`h-full rounded-full transition-all ${BAR_COLORS[item.label]}`}
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {stats.isLoading && (
          <p className="mt-6 text-sm text-muted-foreground">Loading latest data...</p>
        )}
      </div>
    </MainLayout>
  );
}
