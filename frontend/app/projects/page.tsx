import MainLayout from "@/components/layout/MainLayout";
import BrandWatermark from "@/components/common/BrandWatermark";
import { ProjectsPage } from "@/features/projects";
import "@/styles/console-theme.css";

export default function Page() {
  return (
    <MainLayout>
      <div className="console-theme relative isolate -m-8 min-h-[calc(100%+4rem)] overflow-hidden p-8">
        <BrandWatermark />
        <div className="relative z-10">
          <ProjectsPage />
        </div>
      </div>
    </MainLayout>
  );
}