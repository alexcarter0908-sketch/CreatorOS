import { ReactNode } from "react";
import Link from "next/link";

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
}

export default function StatsCard({
  title,
  value,
  description,
  icon,
  loading = false,
  href,
  trendThisWeek,
}: StatsCardProps) {
  const content = (
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
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent text-primary">
          {icon}
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