"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import type { DailyActivityPoint, ContentMixSlice } from "@/lib/hooks/useDashboardStats";

interface AnalyticsSnapshotProps {
  dailyActivity: DailyActivityPoint[];
  contentMix: ContentMixSlice[];
  isLoading?: boolean;
}

const MIX_COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)"];

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-md">
      {label ? <p className="mb-1 font-console-mono text-muted-foreground">{label}</p> : null}
      {payload.map((entry: any) => (
        <p key={entry.name} className="font-console-mono text-foreground">
          {entry.name}: <span className="font-semibold">{entry.value}</span>
        </p>
      ))}
    </div>
  );
}

export default function AnalyticsSnapshot({ dailyActivity, contentMix, isLoading }: AnalyticsSnapshotProps) {
  const totalMix = contentMix.reduce((sum, s) => sum + s.value, 0);

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.4fr_1fr]">
      <div className="rounded-2xl border border-border bg-card p-7 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="font-console-display text-xl font-semibold tracking-tight text-foreground">
            Content Activity
          </h2>
          <span className="text-xs text-muted-foreground">Last 14 days</span>
        </div>

        <div className="mt-5 h-[220px]">
          {isLoading ? (
            <div className="h-full w-full animate-pulse rounded-lg bg-muted" />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyActivity} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                  interval={2}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                  width={28}
                />
                <Tooltip content={<ChartTooltip />} />
                <Area
                  type="monotone"
                  dataKey="count"
                  name="Content created"
                  stroke="var(--chart-1)"
                  strokeWidth={2}
                  fill="url(#activityFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-7 shadow-sm">
        <h2 className="font-console-display text-xl font-semibold tracking-tight text-foreground">
          Content Mix
        </h2>

        <div className="mt-5 h-[220px]">
          {isLoading ? (
            <div className="h-full w-full animate-pulse rounded-lg bg-muted" />
          ) : totalMix === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <p className="text-sm text-muted-foreground">No content generated yet.</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={contentMix}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  strokeWidth={0}
                >
                  {contentMix.map((_, i) => (
                    <Cell key={i} fill={MIX_COLORS[i % MIX_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {totalMix > 0 && (
          <div className="mt-4 flex flex-wrap justify-center gap-x-4 gap-y-1.5">
            {contentMix.map((slice, i) => (
              <span key={slice.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: MIX_COLORS[i % MIX_COLORS.length] }}
                />
                {slice.name} &middot; {slice.value}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
