import { ReactNode } from "react";

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: ReactNode;
  loading?: boolean;
}

export default function StatsCard({
  title,
  value,
  description,
  icon,
  loading = false,
}: StatsCardProps) {
  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-sm transition-all duration-300 hover:shadow-md">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>

          <h2 className="mt-3 text-4xl font-semibold tracking-tight text-foreground">
            {loading ? "-" : value}
          </h2>

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
    </div>
  );
}