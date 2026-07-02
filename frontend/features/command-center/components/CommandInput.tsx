"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { executeAICommand } from "@/lib/ai/gateway";
import { useCommandStore } from "../store/command.store";

export default function CommandInput() {
  const [prompt, setPrompt] = useState("");
  const addCommand = useCommandStore((state) => state.addCommand);

  async function handleSubmit() {
    const value = prompt.trim();

    if (!value) return;

    try {
      const response = await executeAICommand({
        projectId: "",
        command: value,
      });

      addCommand({
        id: crypto.randomUUID(),
        prompt: value,
        status: response.status,
        createdAt: new Date().toISOString(),
      });

      alert(
        `Agent Selected: ${response.agent}\n\n${response.message}`
      );

      setPrompt("");
    } catch (error) {
      console.error(error);
      alert("Failed to execute command");
    }
  }

  return (
    <div className="flex gap-2">
      <Input
        value={prompt}
        placeholder="Type any AI command..."
        onChange={(e) => setPrompt(e.target.value)}
      />

      <Button onClick={handleSubmit}>
        Run
      </Button>
    </div>
  );
}