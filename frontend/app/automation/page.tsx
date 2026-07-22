import MainLayout from "@/components/layout/MainLayout";
import CreateTargetForm from "@/features/automation/components/CreateTargetForm";
import TargetList from "@/features/automation/components/TargetList";

export default function AutomationPage() {
  return (
    <MainLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Automation</h1>
        <p className="mt-2 text-muted-foreground">
          Set a target and Synapse-X-CreatorOS will generate and manage content on autopilot.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <CreateTargetForm />

        <div>
          <h2 className="mb-4 text-lg font-semibold text-foreground">Active Targets</h2>
          <TargetList />
        </div>
      </div>
    </MainLayout>
  );
}
