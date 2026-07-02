"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCommandStore } from "../store/command.store";

export default function CommandInput() {
  const [prompt, setPrompt] = useState("");

  const addCommand = useCommandStore((state) => state.addCommand);

  function handleSubmit() {
    const value = prompt.trim();

    if (!value) return;

    addCommand({
      id: crypto.randomUUID(),
      prompt: value,
      status: "Pending",
      createdAt: new Date().toISOString(),
    });

    setPrompt("");
  }

  return (
    <div className="flex gap-2">
      <Input
        placeholder="Type a command..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <Button onClick={handleSubmit}>
        Run
      </Button>
    </div>
  );
}