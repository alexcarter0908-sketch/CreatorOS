import { create } from "zustand";
import { Command } from "../types/command";
import { getCommands } from "../services/command.service";

interface CommandStore {
  commands: Command[];
  addCommand: (command: Command) => void;
}

export const useCommandStore = create<CommandStore>((set) => ({
  commands: getCommands(),

  addCommand: (command) =>
    set((state) => ({
      commands: [...state.commands, command],
    })),
}));