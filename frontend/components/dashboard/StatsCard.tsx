import { ReactNode } from "react";
import Link from "next/link";
import Sparkline from "./Sparkline";

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: ReactNode;
  loading?: boolean;
  href?: string;
  /** Real count of new items created in the last 7 days. Only rendered
   * when a positive number is provided - never fabricated. */
  trendThisWeek?: number;
  /** Real last-7-day daily counts for this category. When provided (and
   * not all-zero), renders a small trend line under the value. */
  sparkline?: number[];
  sparklineColor?: string;
}

export default function StatsCard({
  title,
  value,
  description,
  icon,
  loading = false,
  href,
  trendThisWeek,
  sparkline,
  sparklineColor = "var(--primary)",
}: StatsCardProps) {
  const content = (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>

          {loading ? (
            <div className="mt-3 h-9 w-16 animate-pulse rounded-md bg-muted" />
          ) : (
            <div className="mt-3 flex items-baseline gap-2">
              <h2 className="font-console-mono text-4xl font-semibold tracking-tight text-foreground">
                {value}
              </h2>
              {typeof trendThisWeek === "number" && trendThisWeek > 0 && (
                <span className="font-console-mono text-xs font-medium text-emerald-400">
                  +{trendThisWeek} this week
                </span>
              )}
            </div>
          )}

          {description && (
            <p className="mt-2 text-sm text-muted-foreground">{description}</p>
          )}
        </div>

        {icon && (
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-accent text-primary">
            {icon}
          </div>
        )}
      </div>

      {!loading && sparkline && sparkline.length > 0 && (
        <div className="mt-4">
          <Sparkline data={sparkline} color={sparklineColor} />
        </div>
      )}
    </div>
  );

  const className =
    "block rounded-2xl border border-border bg-card p-7 shadow-sm transition-all duration-300 hover:shadow-md" +
    (href ? " cursor-pointer hover:border-primary/40 hover:-translate-y-0.5" : "");

  if (href) {
    return (
      <Link href={href} className={className}>
        {content}
      </Link>
    );
  }

  return <div className={className}>{content}</div>;
}