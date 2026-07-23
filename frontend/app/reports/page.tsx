"use client";

import { useEffect, useState } from "react";
import MainLayout from "@/components/layout/MainLayout";
import BrandWatermark from "@/components/common/BrandWatermark";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import apiClient from "@/lib/api/client";
import { Loader2, FileBarChart } from "lucide-react";
import "@/styles/console-theme.css";

interface BreakdownItem {
  asset_type: string;
  label: string;
  count: number;
}

interface UsageReportRow {
  id: string;
  month_label: string;
  total_generations: number;
  failed_generations: number;
  credits_spent: number;
  credits_purchased: number;
  current_balance: number;
  breakdown: BreakdownItem[];
}

export default function ReportsPage() {
  const [reports, setReports] = useState<UsageReportRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get<UsageReportRow[]>("/api/v1/reports")
      .then(({ data }) => setReports(data))
      .catch(() => setReports([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <MainLayout>
      <div className="console-theme relative isolate -m-8 min-h-[calc(100%+4rem)] overflow-hidden p-8">
        <BrandWatermark />
        <div className="relative z-10">
      <DashboardHeader title="Usage Reports" subtitle="Your monthly activity, generated automatically" />

      {loading ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          Loading reports...
        </div>
      ) : reports.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
          <FileBarChart className="mx-auto mb-3 h-8 w-8 opacity-50" />
          No monthly reports yet - your first report will appear here after your first full month of activity.
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((r) => (
            <div key={r.id} className="rounded-2xl border border-border bg-card p-5 shadow-sm">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-lg font-semibold">{r.month_label}</h3>
                <span className="text-sm text-muted-foreground">
                  {r.total_generations} total generations
                </span>
              </div>

              <div className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
                <div className="rounded-lg bg-muted/60 p-3">
                  <div className="text-xs text-muted-foreground">Credits Used</div>
                  <div className="text-lg font-semibold">{r.credits_spent}</div>
                </div>
                <div className="rounded-lg bg-muted/60 p-3">
                  <div className="text-xs text-muted-foreground">Credits Purchased</div>
                  <div className="text-lg font-semibold">{r.credits_purchased}</div>
                </div>
                <div className="rounded-lg bg-muted/60 p-3">
                  <div className="text-xs text-muted-foreground">Current Balance</div>
                  <div className="text-lg font-semibold">{r.current_balance}</div>
                </div>
                <div className="rounded-lg bg-muted/60 p-3">
                  <div className="text-xs text-muted-foreground">Failed</div>
                  <div className="text-lg font-semibold">{r.failed_generations}</div>
                </div>
              </div>

              <div className="space-y-1.5">
                {r.breakdown.map((item) => (
                  <div key={item.asset_type} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{item.label}</span>
                    <span className="font-medium">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
        </div>
      </div>
    </MainLayout>
  );
}