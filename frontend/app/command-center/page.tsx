import CommandInput from "@/features/command-center/components/CommandInput";
import CommandHistory from "@/features/command-center/components/CommandHistory";

export default function CommandCenterPage() {
  return (
    <main className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Command Center
        </h1>

        <p className="mt-2 text-slate-500">
          Give CreatorOS a command and monitor execution history.
        </p>
      </div>

      <CommandInput />

      <CommandHistory />
    </main>
  );
}