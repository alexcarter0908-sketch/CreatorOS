import { executeAICommand } from "@/lib/ai/gateway";

export async function submitCommand(
  projectId: string,
  command: string
) {
  return executeAICommand({
    projectId,
    command,
  });
}