"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { submitCommand } from "../services/command.service";
import { useCommandStore } from "../store/command.store";

export default function CommandInput() {
  const [prompt, setPrompt] = useState("");

  const addCommand = useCommandStore((state) => state.addCommand);

  async function handleSubmit() {
    const value = prompt.trim();

    if (!value) return;

    try {
      const result = await submitCommand(
        "demo-project",
        value
      );

      addCommand({
        id: result.executionId,
        prompt: value,
        status: result.status,
        createdAt: new Date().toISOString(),
      });

      setPrompt("");
    } catch (error) {
      console.error(error);
      alert("Failed to execute command.");
    }
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