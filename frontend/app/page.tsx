import Link from "next/link";

import MainLayout from "../components/layout/MainLayout";
import DashboardHeader from "../components/dashboard/DashboardHeader";
import StatsCard from "../components/dashboard/StatsCard";
import QuickActions from "../components/dashboard/QuickActions";

import {
  FolderKanban,
  FileText,
  Video,
  Coins,
  Terminal,
} from "lucide-react";

export default function Home() {
  return (
    <MainLayout>
      <DashboardHeader
        title="Dashboard"
        subtitle="Welcome back to CreatorOS 👋"
      />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatsCard
          title="Projects"
          value="12"
          description="Active projects"
          icon={<FolderKanban className="h-7 w-7 text-blue-600" />}
        />

        <StatsCard
          title="Scripts"
          value="48"
          description="Generated scripts"
          icon={<FileText className="h-7 w-7 text-green-600" />}
        />

        <StatsCard
          title="Videos"
          value="19"
          description="Videos created"
          icon={<Video className="h-7 w-7 text-purple-600" />}
        />

        <StatsCard
          title="Credits"
          value="980"
          description="Credits remaining"
          icon={<Coins className="h-7 w-7 text-yellow-600" />}
        />
      </div>

      <div className="mt-8">
        <QuickActions />
      </div>

      <div className="mt-8 rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <Terminal className="h-6 w-6 text-blue-600" />

          <div>
            <h2 className="text-xl font-semibold">
              Command Center
            </h2>

            <p className="text-sm text-slate-500">
              Control CreatorOS using natural language commands.
            </p>
          </div>
        </div>

        <div className="mt-6">
          <Link
            href="/command-center"
            className="inline-flex rounded-lg bg-black px-4 py-2 text-white transition hover:bg-slate-800"
          >
            Open Command Center
          </Link>
        </div>
      </div>
    </MainLayout>
  );
}