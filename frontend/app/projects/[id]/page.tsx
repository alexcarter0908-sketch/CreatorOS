import MainLayout from "@/components/layout/MainLayout";
import { ProjectDetail } from "@/features/projects";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function Page({ params }: PageProps) {
  const { id } = await params;

  return (
    <MainLayout>
      <ProjectDetail id={id} />
    </MainLayout>
  );
}
