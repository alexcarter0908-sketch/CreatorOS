interface DashboardHeaderProps {
  title: string;
  subtitle: string;
}

export default function DashboardHeader({
  title,
  subtitle,
}: DashboardHeaderProps) {
  return (
    <div className="mb-10">
      <h1 className="text-4xl font-semibold tracking-tight text-foreground">
        {title}
      </h1>
      <p className="mt-2 text-lg text-muted-foreground">{subtitle}</p>
    </div>
  );
}
