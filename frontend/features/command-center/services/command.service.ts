import { executeAICommand, type AICommandHistoryTurn, type AICommandResponse } from "@/lib/ai/gateway";
import { API_BASE_URL, ACCESS_TOKEN_KEY } from "@/lib/api/client";
import { getAsset } from "@/features/assets/services/asset.service";
import type { Asset } from "@/features/assets/types/asset";

export interface RunCommandResult {
  assetId: string;
  asset: Asset;
  conversationId: string;
}

const CONVERSATION_KEY = "creatoros_active_conversation";

export function getStoredConversationId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(CONVERSATION_KEY);
}

export function setStoredConversationId(id: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(CONVERSATION_KEY, id);
}

export function clearStoredConversationId() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(CONVERSATION_KEY);
}

export interface RunCommandStreamCallbacks {
  onToken: (delta: string) => void;
  onDone: (asset: Asset) => void;
  onError?: (message: string) => void;
}

export interface StreamStoppedResult {
  stopped: true;
  partialText: string;
}

/**
 * Real token-by-token streaming via the backend's SSE endpoint
 * (/api/v1/commands/run/stream). Reads the raw response body stream,
 * parses SSE "event:"/"data:" frames as they arrive, and invokes the
 * matching callback per event -- no simulation, no buffering of the
 * full response before displaying it.
 *
 * `signal` (optional) lets the caller cancel generation at any time
 * (e.g. a Stop button) - when aborted, this resolves with
 * { stopped: true, partialText } instead of throwing, so the partial
 * response stays visible and the UI can offer a "Continue" option.
 */
export async function runCommandStream(
  command: string,
  history: AICommandHistoryTurn[] = [],
  callbacks: RunCommandStreamCallbacks,
  signal?: AbortSignal
): Promise<RunCommandResult | StreamStoppedResult> {
  const conversationId = getStoredConversationId();
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem(ACCESS_TOKEN_KEY)
      : null;

  const response = await fetch(`${API_BASE_URL}/api/v1/commands/run/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      command,
      project_id: null,
      conversation_id: conversationId,
      history,
    }),
    signal,
  });

  if (!response.ok || !response.body) {
    const message = `Request failed (${response.status}).`;
    callbacks.onError?.(message);
    throw new Error(message);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  let finalAssetId: string | null = null;
  let finalConversationId: string | null = conversationId;
  let finalStatus = "completed";
  let sawError: string | null = null;
  let accumulatedText = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        if (!frame.trim()) continue;

        let eventName = "message";
        let dataLine = "";

        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) {
            eventName = line.slice("event:".length).trim();
          } else if (line.startsWith("data:")) {
            dataLine = line.slice("data:".length).trim();
          }
        }

        if (!dataLine) continue;

        let parsed: Record<string, unknown>;
        try {
          parsed = JSON.parse(dataLine);
        } catch {
          continue;
        }

        if (eventName === "token" && typeof parsed.text === "string") {
          accumulatedText += parsed.text;
          callbacks.onToken(parsed.text);
        } else if (eventName === "done") {
          finalAssetId = (parsed.asset_id as string) ?? null;
          finalConversationId = (parsed.conversation_id as string) ?? finalConversationId;
          finalStatus = (parsed.status as string) ?? "completed";
        } else if (eventName === "error") {
          sawError = (parsed.detail as string) ?? "Streaming request failed.";
        }
      }
    }
  } catch (error) {
    const isAbort =
      (error instanceof DOMException && error.name === "AbortError") ||
      (signal?.aborted ?? false);
    if (isAbort) {
      // User hit Stop - this is not a failure, just an early cutoff.
      // Cancelling the reader tells the browser to close the
      // underlying connection instead of leaving it dangling.
      try {
        await reader.cancel();
      } catch {
        // ignore - connection is being torn down anyway
      }
      return { stopped: true, partialText: accumulatedText };
    }
    throw error;
  }

  if (sawError) {
    callbacks.onError?.(sawError);
    throw new Error(sawError);
  }

  if (!finalAssetId) {
    const message = "No asset id returned from streaming command.";
    callbacks.onError?.(message);
    throw new Error(message);
  }

  if (finalConversationId) {
    setStoredConversationId(finalConversationId);
  }

  const asset = await getAsset(finalAssetId);
  callbacks.onDone(asset);

  return {
    assetId: finalAssetId,
    asset,
    conversationId: finalConversationId ?? "",
  };
}

/**
 * Runs a command via the buffered endpoint. Two shapes come back:
 *  - normal: { asset_id, conversation_id, ... } - fetches the asset
 *    and returns it as usual.
 *  - multi-step pipeline: { workflow_id, status: "running", asset_id: null }
 *    - no asset yet, so this returns the raw response instead of
 *      throwing, letting the caller (CommandInput) detect
 *      `workflow_id` and start polling /api/v1/workflows/{id}.
 */
export async function runCommand(
  command: string,
  history: AICommandHistoryTurn[] = [],
  location?: { latitude: number; longitude: number } | null
): Promise<RunCommandResult | AICommandResponse> {
  const conversationId = getStoredConversationId();

  const response = await executeAICommand({
    projectId: "",
    command,
    conversationId,
    history,
    latitude: location?.latitude ?? null,
    longitude: location?.longitude ?? null,
  });

  if (response.conversation_id) {
    setStoredConversationId(response.conversation_id);
  }

  if (response.workflow_id) {
    return response;
  }

  const assetId = response.asset_id;
  if (!assetId) {
    throw new Error("No asset id returned from command.");
  }

  const asset = await getAsset(assetId);
  return { assetId, asset, conversationId: response.conversation_id ?? "" };
}