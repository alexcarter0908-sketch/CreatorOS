import { create } from "zustand";

import type { Command } from "../types/command";

interface CommandStore {
  commands: Command[];
  addCommand: (command: Command) => void;
}

export const useCommandStore = create<CommandStore>((set) => ({
  commands: [],

  addCommand: (command) =>
    set((state) => ({
      commands: [...state.commands, command],
    })),
}));