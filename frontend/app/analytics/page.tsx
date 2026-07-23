"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import MainLayout from "@/components/layout/MainLayout";
import BrandWatermark from "@/components/common/BrandWatermark";
import { useDashboardStats } from "@/lib/hooks/useDashboardStats";
import "@/styles/console-theme.css";

const COLORS: Record<string, string> = {
  Scripts: "#22c55e", // green-500
  Videos: "#a855f7", // purple-500
  Images: "#3b82f6", // blue-500
  Audio: "#f97316", // orange-500
};

export default function AnalyticsPage() {
  const stats = useDashboardStats();

  const breakdown = [
    { name: "Scripts", value: stats.scripts },
    { name: "Videos", value: stats.videos },
    { name: "Images", value: stats.images },
    { name: "Audio", value: stats.audio },
  ];

  const total = breakdown.reduce((sum, item) => sum + item.value, 0);
  const hasData = total > 0;

  return (
    <MainLayout>
      <div className="console-theme relative isolate -m-8 min-h-[calc(100%+4rem)] overflow-hidden p-8">
        <BrandWatermark />
        <div className="relative z-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
        <p className="mt-2 text-muted-foreground">
          A breakdown of everything Synapse-X-CreatorOS has generated for you.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* ---- Distribution: pie chart ---- */}
        <div className="rounded-2xl border bg-card p-6 shadow-sm">
          <h2 className="mb-1 text-lg font-semibold text-foreground">Content Distribution</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Share of each content type out of {total} total item{total === 1 ? "" : "s"}.
          </p>

          {hasData ? (
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={breakdown}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                  >
                    {breakdown.map((item) => (
                      <Cell key={item.name} fill={COLORS[item.name]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${value} (${total > 0 ? Math.round((value / total) * 100) : 0}%)`,
                      name,
                    ]}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-72 items-center justify-center text-sm text-muted-foreground">
              No content generated yet.
            </div>
          )}
        </div>

        {/* ---- Totals: bar chart ---- */}
        <div className="rounded-2xl border bg-card p-6 shadow-sm">
          <h2 className="mb-1 text-lg font-semibold text-foreground">Totals by Type</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Raw count generated per content type.
          </p>

          {hasData ? (
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={breakdown}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {breakdown.map((item) => (
                      <Cell key={item.name} fill={COLORS[item.name]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex h-72 items-center justify-center text-sm text-muted-foreground">
              No content generated yet.
            </div>
          )}
        </div>
      </div>

      {/* ---- Credits ---- */}
      <div className="mt-6 rounded-2xl border bg-card p-6 shadow-sm">
        <h2 className="mb-1 text-lg font-semibold text-foreground">Credits</h2>
        <p className="text-sm text-muted-foreground">Your current available balance.</p>
        <p className="mt-3 text-3xl font-bold text-foreground">{stats.credits}</p>
      </div>

      {stats.isLoading && (
        <p className="mt-6 text-sm text-muted-foreground">Loading latest data...</p>
      )}
        </div>
      </div>
    </MainLayout>
  );
}
