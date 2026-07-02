"use client";

import { useCommandStore } from "../store/command.store";

export default function CommandHistory() {
  const commands = useCommandStore((state) => state.commands);

  if (commands.length === 0) {
    return (
      <div className="rounded-xl border border-dashed p-6 text-center text-sm text-slate-500">
        No commands yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {commands
        .slice()
        .reverse()
        .map((command) => (
          <div
            key={command.id}
            className="rounded-xl border p-4"
          >
            <p className="font-medium">
              {command.prompt}
            </p>

            <div className="mt-2 flex items-center justify-between text-sm text-slate-500">
              <span>{command.status}</span>

              <span>
                {new Date(command.createdAt).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
    </div>
  );
}