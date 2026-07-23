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

import type { DailyTypeBreakdownPoint, ContentMixSlice } from "@/lib/hooks/useDashboardStats";

interface AnalyticsSnapshotProps {
  dailyActivityByType: DailyTypeBreakdownPoint[];
  contentMix: ContentMixSlice[];
  isLoading?: boolean;
}

// Scripts / Images / Videos / Audio - same order + colors used by the
// Content Mix donut below, so the two panels read consistently.
const SERIES = [
  { key: "scripts", name: "Scripts", color: "var(--chart-1)" },
  { key: "images", name: "Images", color: "var(--chart-2)" },
  { key: "videos", name: "Videos", color: "var(--chart-3)" },
  { key: "audio", name: "Audio", color: "var(--chart-4)" },
] as const;

const MIX_COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)"];

interface TooltipPayloadEntry {
  name: string;
  value: number;
  color: string;
}

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const nonZero = payload.filter((entry) => entry.value > 0);
  if (nonZero.length === 0) return null;
  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-md">
      {label ? <p className="mb-1.5 font-console-mono text-muted-foreground">{label}</p> : null}
      {nonZero.map((entry) => (
        <p key={entry.name} className="flex items-center gap-1.5 font-console-mono text-foreground">
          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: entry.color }} />
          {entry.name}: <span className="font-semibold">{entry.value}</span>
        </p>
      ))}
    </div>
  );
}

export default function AnalyticsSnapshot({ dailyActivityByType, contentMix, isLoading }: AnalyticsSnapshotProps) {
  const totalMix = contentMix.reduce((sum, s) => sum + s.value, 0);
  const hasActivity = dailyActivityByType.some((d) => d.scripts + d.images + d.videos + d.audio > 0);

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.6fr_1fr]">
      <div className="rounded-2xl border border-border bg-card p-7 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-console-display text-xl font-semibold tracking-tight text-foreground">
            Content Activity
          </h2>
          <div className="flex items-center gap-4">
            {SERIES.map((s) => (
              <span key={s.key} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: s.color }} />
                {s.name}
              </span>
            ))}
          </div>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">Last 14 days, by content type</p>

        <div className="mt-5 h-[300px]">
          {isLoading ? (
            <div className="h-full w-full animate-pulse rounded-lg bg-muted" />
          ) : !hasActivity ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <p className="text-sm text-muted-foreground">No content generated yet in this window.</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyActivityByType} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  {SERIES.map((s) => (
                    <linearGradient key={s.key} id={`fill-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={s.color} stopOpacity={0.3} />
                      <stop offset="100%" stopColor={s.color} stopOpacity={0} />
                    </linearGradient>
                  ))}
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
                {SERIES.map((s) => (
                  <Area
                    key={s.key}
                    type="monotone"
                    dataKey={s.key}
                    name={s.name}
                    stroke={s.color}
                    strokeWidth={2}
                    fill={`url(#fill-${s.key})`}
                  />
                ))}
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
