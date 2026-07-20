New-Item -ItemType Directory -Force -Path "C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\frontend\app\assets" | Out-Null
$cmdContent = @'
"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import axios from "axios";
import {
  Send,
  Plus,
  Image as ImageIcon,
  Video,
  Music,
  FileText,
  Mic,
  X,
  Loader2,
  Paperclip,
  Copy,
  Pencil,
  CornerUpLeft,
  Check,
  ChevronDown,
  Square,
  Link2,
  Download,
  FileCode2,
  RefreshCw,
  Star,
  Layers,
  Wand2,
  CreditCard,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import apiClient from "@/lib/api/client";
import { useCommandStore } from "../store/command.store";
import { runCommand } from "../services/command.service";
import { fetchConversation } from "../services/conversation.service";
import { getStoredConversationId } from "../services/command.service";
import { getAsset } from "@/features/assets/services/asset.service";
import type { ChatMessage, ChatAttachment, AttachmentKind, ChatSource } from "../types/command";
import type { AICommandHistoryTurn } from "@/lib/ai/gateway";
import { clearStoredConversationId } from "../services/command.service";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MIN_TEXTAREA_HEIGHT = 44;
const MAX_TEXTAREA_HEIGHT = 200;
const PASTE_LINE_THRESHOLD = 500;
const COLLAPSE_LENGTH = 500;
const COLLAPSE_LINES = 500;
const WAVE_BAR_COUNT = 28;
const TEMPLATES_STORAGE_KEY = "creatoros_prompt_templates";
const PROVIDER_STATUS_STORAGE_KEY = "creatoros_provider_status";

// NOTE: word order matters here - the backend's actual message is
// "No provider available for asset type '...'" (provider comes before
// available). Getting this backwards means the pattern never matches
// and the upgrade prompt never shows.
const NEEDS_UPGRADE_PATTERN = /no provider available|insufficient credits|configure api key/i;

// Never show raw backend/provider error text (e.g. "PixVerse request
// failed (400): {...}") to the user - it exposes internal system
// faults. Always translate to a calm, friendly line instead.
function getDisplayErrorMessage(raw: string | null | undefined): string {
  if (raw && NEEDS_UPGRADE_PATTERN.test(raw)) {
    return "This generation needs more credits or a plan upgrade to continue.";
  }
  return "Something went wrong on our end. Please try again in a moment.";
}

// Asset types that get the dedicated "artifact card" treatment instead
// of being rendered as a plain chat bubble - these are generated
// deliverables (a script, an SEO package, a document) the user is meant
// to copy/download and reuse, not read as a conversational reply.
const CARD_ASSET_TYPES = new Set(["script", "document", "seo"]);

function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string" && detail) return detail;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

function buildHistory(messages: ChatMessage[]): AICommandHistoryTurn[] {
  return messages
    .filter((m) => m.status === "completed" && m.content.trim().length > 0)
    .slice(-20)
    .map((m) => ({ role: m.role, content: m.content }));
}

function getAttachmentKind(file: File): AttachmentKind {
  if (file.type.startsWith("image/")) return "image";
  if (file.type.startsWith("video/")) return "video";
  if (file.type.startsWith("audio/")) return "audio";
  return "document";
}

interface PendingAttachment {
  id: string;
  file: File;
  url: string;
  kind: AttachmentKind;
}

interface PromptTemplate {
  id: string;
  label: string;
  text: string;
}

function loadTemplates(): PromptTemplate[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(TEMPLATES_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as PromptTemplate[]) : [];
  } catch {
    return [];
  }
}

function saveTemplates(templates: PromptTemplate[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TEMPLATES_STORAGE_KEY, JSON.stringify(templates));
}

interface ProviderStatusMap {
  [assetType: string]: { ok: boolean; updatedAt: string };
}

function loadProviderStatus(): ProviderStatusMap {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(PROVIDER_STATUS_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ProviderStatusMap) : {};
  } catch {
    return {};
  }
}

function recordProviderStatus(assetType: string, ok: boolean) {
  if (typeof window === "undefined") return;
  const current = loadProviderStatus();
  current[assetType] = { ok, updatedAt: new Date().toISOString() };
  localStorage.setItem(PROVIDER_STATUS_STORAGE_KEY, JSON.stringify(current));
}

/* ---------- Code block with copy ---------- */
function CodeBlock({ code, lang, onCopy }: { code: string; lang?: string; onCopy: (t: string) => void }) {
  return (
    <div className="my-2 overflow-hidden rounded-lg border border-code-border bg-code text-xs">
      {lang ? (
        <div className="border-b border-code-border px-3 py-1 text-[10px] uppercase tracking-wide text-code-foreground/60">
          {lang}
        </div>
      ) : null}
      <div className="relative">
        <pre className="overflow-x-auto whitespace-pre-wrap p-3 text-code-foreground">
          <code>{code}</code>
        </pre>
        <button
          onClick={() => onCopy(code)}
          className="absolute right-2 top-2 rounded-md bg-black/20 p-1.5 text-code-foreground/70 hover:bg-black/30 hover:text-code-foreground"
          title="Copy code"
        >
          <Copy className="h-3 w-3" />
        </button>
      </div>
    </div>
  );
}

/* ---------- Markdown styling for AI responses ---------- */
const markdownComponents = {
  h1: (props: any) => <h1 className="mt-3 mb-2 text-lg font-bold text-foreground first:mt-0" {...props} />,
  h2: (props: any) => <h2 className="mt-3 mb-2 text-base font-bold text-foreground first:mt-0" {...props} />,
  h3: (props: any) => <h3 className="mt-2 mb-1 text-sm font-bold uppercase tracking-wide text-foreground first:mt-0" {...props} />,
  p: (props: any) => <p className="mb-2 whitespace-pre-wrap leading-relaxed last:mb-0" {...props} />,
  strong: (props: any) => <strong className="font-semibold text-foreground" {...props} />,
  em: (props: any) => <em className="italic" {...props} />,
  ul: (props: any) => <ul className="mb-2 ml-4 list-disc space-y-1 last:mb-0" {...props} />,
  ol: (props: any) => <ol className="mb-2 ml-4 list-decimal space-y-1 last:mb-0" {...props} />,
  li: (props: any) => <li className="leading-relaxed" {...props} />,
  hr: () => <hr className="my-3 border-border" />,
  blockquote: (props: any) => <blockquote className="my-2 border-l-4 border-primary/40 pl-3 italic text-muted-foreground" {...props} />,
  a: (props: any) => (
    <a className="text-primary underline hover:no-underline" target="_blank" rel="noreferrer" {...props} />
  ),
};

/* ---------- Collapsible long text ---------- */
function CollapsibleText({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const lineCount = text.split("\n").length;
  const isLong = lineCount > COLLAPSE_LINES;

  if (!isLong) {
    return (
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
        {text}
      </ReactMarkdown>
    );
  }

  return (
    <div className="my-1 overflow-hidden rounded-lg border border-border bg-muted/50">
      <div className={`p-3 text-sm leading-relaxed ${expanded ? "" : "max-h-32 overflow-hidden"}`}>
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
          {text}
        </ReactMarkdown>
      </div>
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-center gap-1 border-t border-border py-1.5 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
      >
        <ChevronDown className={`h-3 w-3 transition-transform ${expanded ? "rotate-180" : ""}`} />
        {expanded ? "Show less" : "Show more"}
      </button>
    </div>
  );
}

function parseSegments(content: string) {
  const parts = content.split(/(```[\s\S]*?```)/g);
  const segments: { type: "code" | "text"; content: string; lang?: string }[] = [];
  for (const part of parts) {
    if (!part) continue;
    if (part.startsWith("```")) {
      const match = part.match(/```(\w+)?\n?([\s\S]*?)```$/);
      segments.push({
        type: "code",
        lang: match?.[1] ?? "",
        content: (match?.[2] ?? part.replace(/```/g, "")).replace(/\n$/, ""),
      });
    } else if (part.trim()) {
      segments.push({ type: "text", content: part });
    }
  }
  return segments;
}

function renderContent(content: string, onCopy: (t: string) => void, collapsible: boolean) {
  return parseSegments(content).map((seg, i) =>
    seg.type === "code" ? (
      <CodeBlock key={i} code={seg.content} lang={seg.lang} onCopy={onCopy} />
    ) : collapsible ? (
      <CollapsibleText key={i} text={seg.content} />
    ) : (
      <div key={i}>
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
          {seg.content}
        </ReactMarkdown>
      </div>
    )
  );
}

const ASSET_TYPE_LABELS: Record<string, string> = {
  script: "Script",
  document: "Document",
  seo: "SEO Package",
};

/* ---------- Artifact-style card for scripts / documents / SEO packages ---------- */
function GeneratedContentCard({
  content,
  assetType,
  fileUrl,
  onCopy,
}: {
  content: string;
  assetType: string;
  fileUrl?: string | null;
  onCopy: (t: string) => void;
}) {
  const label = ASSET_TYPE_LABELS[assetType] ?? "Generated Content";

  return (
    <div className="my-1 w-full max-w-full overflow-hidden rounded-xl border border-border bg-background shadow-sm">
      <div className="flex items-center justify-between border-b border-border bg-muted/60 px-3 py-2">
        <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
          <FileCode2 className="h-3.5 w-3.5" />
          {label}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onCopy(content)}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            title="Copy"
          >
            <Copy className="h-3.5 w-3.5" />
            Copy
          </button>
          {fileUrl ? (
            <a
              href={fileUrl}
              download
              className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              title="Download"
            >
              <Download className="h-3.5 w-3.5" />
              Download
            </a>
          ) : null}
        </div>
      </div>
      <div className="max-h-[420px] overflow-y-auto p-4 text-[15px] leading-relaxed">
        {renderContent(content, onCopy, false)}
      </div>
    </div>
  );
}

function AttachmentPreview({ attachment }: { attachment: ChatAttachment }) {
  if (attachment.kind === "image") {
    return <img src={attachment.url} alt={attachment.name} className="max-h-56 rounded-lg border border-border object-cover" />;
  }
  if (attachment.kind === "video") {
    return <video src={attachment.url} controls className="max-h-56 w-full rounded-lg border border-border" />;
  }
  if (attachment.kind === "audio") {
    return <audio src={attachment.url} controls className="w-full" />;
  }
  return (
    <a href={attachment.url} target="_blank" rel="noreferrer" className="flex items-center gap-2 rounded-lg border border-border bg-muted px-3 py-2 text-sm hover:bg-accent">
      <FileText className="h-4 w-4 shrink-0" />
      <span className="truncate">{attachment.name}</span>
    </a>
  );
}

/* ---------- Feature 3: Provider status indicator ---------- */
function ProviderStatusBar({ status }: { status: ProviderStatusMap }) {
  const entries = Object.entries(status);
  if (entries.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 border-b border-border bg-muted/40 px-4 py-1.5 text-[11px]">
      <span className="font-medium text-muted-foreground">Status:</span>
      {entries.map(([assetType, s]) => (
        <span
          key={assetType}
          className={`flex items-center gap-1 rounded-full px-2 py-0.5 font-medium ${
            s.ok ? "bg-emerald-500/10 text-emerald-600" : "bg-destructive/10 text-destructive"
          }`}
          title={new Date(s.updatedAt).toLocaleString()}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${s.ok ? "bg-emerald-500" : "bg-destructive"}`} />
          {assetType}
        </span>
      ))}
    </div>
  );
}

export default function CommandInput() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [attachMenuOpen, setAttachMenuOpen] = useState(false);
  const [attachments, setAttachments] = useState<PendingAttachment[]>([]);
  const [pastedBlock, setPastedBlock] = useState<string | null>(null);
  const [pastedBlockExpanded, setPastedBlockExpanded] = useState(false);
  const [replyTo, setReplyTo] = useState<string | null>(null);
  const [selectionPopup, setSelectionPopup] = useState<{ x: number; y: number; text: string } | null>(null);
  const [waveLevels, setWaveLevels] = useState<number[]>(Array(WAVE_BAR_COUNT).fill(3));
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());

  // Feature 4: prompt templates
  const [templates, setTemplatesState] = useState<PromptTemplate[]>([]);
  // Single combined popover (opened from the icon button next to Mic)
  // that holds: saved templates list, "save current as template", and
  // the batch-variations toggle - keeps the toolbar from being cluttered.
  const [toolsOpen, setToolsOpen] = useState(false);

  // Feature 3: provider status (client-side memory of last known result per asset type)
  const [providerStatus, setProviderStatus] = useState<ProviderStatusMap>({});

  // Feature 6: batch/bulk generation
  const [batchMode, setBatchMode] = useState(false);
  const BATCH_COUNT = 3;

  useEffect(() => {
    setTemplatesState(loadTemplates());
    setProviderStatus(loadProviderStatus());
  }, []);

  function toggleSources(messageId: string) {
    setExpandedSources((prev) => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  }

  const messages = useCommandStore((s) => s.messages);
  const addMessage = useCommandStore((s) => s.addMessage);
  const updateMessage = useCommandStore((s) => s.updateMessage);
  const clearMessages = useCommandStore((s) => s.clearMessages);
  const setMessages = useCommandStore((s) => s.setMessages);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const acceptRef = useRef<string>("*/*");

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    const next = Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT);
    el.style.height = `${Math.max(next, MIN_TEXTAREA_HEIGHT)}px`;
  }, [prompt]);

  useEffect(() => {
    const prefill = searchParams.get("prefill");
    if (prefill) setPrompt(prefill);
  }, [searchParams]);

  useEffect(() => {
    const id = getStoredConversationId();
    if (!id) return;
    fetchConversation(id)
      .then((msgs) => {
        if (msgs.length > 0) {
          setMessages(msgs);
          setExpandedSources((prev) => {
            const next = new Set(prev);
            for (const m of msgs) {
              if (m.sources && m.sources.length > 0) next.add(m.id);
            }
            return next;
          });
        }
      })
      .catch(() => {
        clearStoredConversationId();
      });
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  function handlePaste(e: React.ClipboardEvent<HTMLTextAreaElement>) {
    const text = e.clipboardData.getData("text");
    const lineCount = text.split("\n").length;
    if (lineCount > PASTE_LINE_THRESHOLD) {
      e.preventDefault();
      setPastedBlock((prev) => (prev ? `${prev}\n${text}` : text));
      setPastedBlockExpanded(false);
    }
  }

  function handleCopy(text: string) {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard.");
  }

  function handleEdit(text: string) {
    setPrompt(text);
    requestAnimationFrame(() => textareaRef.current?.focus());
  }

  function handleBubbleMouseUp() {
    const sel = window.getSelection();
    const text = sel?.toString().trim() ?? "";
    if (!text || !sel || sel.rangeCount === 0) {
      setSelectionPopup(null);
      return;
    }
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    setSelectionPopup({ x: rect.left + rect.width / 2, y: rect.top - 8, text });
  }

  function confirmReply() {
    if (selectionPopup) {
      setReplyTo(selectionPopup.text);
      setSelectionPopup(null);
      window.getSelection()?.removeAllRanges();
      requestAnimationFrame(() => textareaRef.current?.focus());
    }
  }

  function openFilePicker(accept: string) {
    acceptRef.current = accept;
    if (fileInputRef.current) {
      fileInputRef.current.accept = accept;
      fileInputRef.current.click();
    }
    setAttachMenuOpen(false);
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    const next: PendingAttachment[] = files.map((file) => ({
      id: crypto.randomUUID(),
      file,
      url: URL.createObjectURL(file),
      kind: getAttachmentKind(file),
    }));
    setAttachments((prev) => [...prev, ...next]);
    e.target.value = "";
  }

  function removeAttachment(id: string) {
    setAttachments((prev) => {
      const found = prev.find((a) => a.id === id);
      if (found) URL.revokeObjectURL(found.url);
      return prev.filter((a) => a.id !== id);
    });
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      audioChunksRef.current = [];

      const audioContext = new AudioContext();
      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.6;
      source.connect(analyser);
      audioContextRef.current = audioContext;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      function updateLevels() {
        analyser.getByteFrequencyData(dataArray);
        const usableBins = Math.floor(dataArray.length * 0.6);
        const chunkSize = Math.max(1, Math.floor(usableBins / WAVE_BAR_COUNT));
        const levels = Array.from({ length: WAVE_BAR_COUNT }, (_, i) => {
          const start = i * chunkSize;
          let sum = 0;
          let count = 0;
          for (let j = start; j < start + chunkSize && j < usableBins; j++) {
            sum += dataArray[j];
            count++;
          }
          const avg = count > 0 ? sum / count : 0;
          const normalized = avg / 255;
          const boosted = Math.pow(normalized, 0.6);
          return Math.max(4, Math.min(40, boosted * 40));
        });
        setWaveLevels(levels);
        animationFrameRef.current = requestAnimationFrame(updateLevels);
      }
      updateLevels();

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const file = new File([blob], `voice-${Date.now()}.webm`, { type: "audio/webm" });
        stream.getTracks().forEach((t) => t.stop());
        if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
        audioContext.close();
        setWaveLevels(Array(WAVE_BAR_COUNT).fill(3));

        try {
          const formData = new FormData();
          formData.append("file", file);
          const { data } = await apiClient.post<{ text: string }>(
            "/api/v1/commands/transcribe",
            formData,
            { headers: { "Content-Type": undefined } }
          );
          if (data?.text) {
            setPrompt((prev) => (prev ? `${prev} ${data.text}` : data.text));
            requestAnimationFrame(() => textareaRef.current?.focus());
          }
        } catch {
          toast.error("Could not transcribe voice. Please try again.");
        }
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch {
      toast.error("Microphone access denied.");
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  }

  // Feature 1: retry - resubmits the exact prompt that produced a
  // failed assistant message. Looks up the preceding user message by
  // walking backwards from the failed message's position.
  function handleRetry(assistantMessageId: string) {
    const idx = messages.findIndex((m) => m.id === assistantMessageId);
    if (idx === -1) return;
    let userText: string | null = null;
    for (let i = idx - 1; i >= 0; i--) {
      if (messages[i].role === "user") {
        userText = messages[i].content;
        break;
      }
    }
    if (!userText) {
      toast.error("Could not find the original message to retry.");
      return;
    }
    submitPrompt(userText);
  }

  // Feature 4: templates
  function saveCurrentAsTemplate() {
    const text = prompt.trim();
    if (!text) {
      toast.error("Type a prompt first, then save it as a template.");
      return;
    }
    const label = text.length > 40 ? `${text.slice(0, 40)}...` : text;
    const next = [...templates, { id: crypto.randomUUID(), label, text }];
    setTemplatesState(next);
    saveTemplates(next);
    toast.success("Saved as template.");
  }

  function useTemplate(t: PromptTemplate) {
    setPrompt(t.text);
    setToolsOpen(false);
    requestAnimationFrame(() => textareaRef.current?.focus());
  }

  function deleteTemplate(id: string) {
    const next = templates.filter((t) => t.id !== id);
    setTemplatesState(next);
    saveTemplates(next);
  }

  // Shared submit path used by the normal send button, retry, and batch.
  async function submitPrompt(value: string, attachmentsOverride?: PendingAttachment[]) {
    const activeAttachments = attachmentsOverride ?? [];
    if (!value.trim() && activeAttachments.length === 0) return;

    const history = buildHistory(messages);
    const chatAttachments: ChatAttachment[] | undefined =
      activeAttachments.length > 0
        ? activeAttachments.map((a) => ({ id: a.id, url: a.url, kind: a.kind, name: a.file.name }))
        : undefined;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: value,
      createdAt: new Date().toISOString(),
      status: "completed",
      attachments: chatAttachments,
    };
    const assistantId = crypto.randomUUID();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
      status: "pending",
    };
    addMessage(userMessage);
    addMessage(assistantMessage);

    try {
      const response = await runCommand(value || "Sent attachment(s)", history);

      if ("workflow_id" in response && response.workflow_id) {
        pollWorkflow(response.workflow_id, assistantId);
        return;
      }

      const { asset } = response as { asset: import("@/features/assets/types/asset").Asset };
      const meta = (asset.extra_metadata ?? {}) as Record<string, unknown>;
      const text =
        (typeof meta.text === "string" && meta.text) ||
        (typeof meta.raw_result === "string" && meta.raw_result) ||
        (typeof meta.result === "string" && meta.result) ||
        "";
      const sources = Array.isArray(meta.sources) ? (meta.sources as ChatSource[]) : undefined;

      updateMessage(assistantId, {
        content: text,
        status: asset.status === "failed" ? "failed" : "completed",
        assetType: asset.asset_type,
        fileUrl: asset.file_url,
        errorMessage: asset.error_message,
        sources,
      });

      if (sources && sources.length > 0) {
        setExpandedSources((prev) => new Set(prev).add(assistantId));
      }

      if (asset.asset_type) {
        recordProviderStatus(asset.asset_type, asset.status !== "failed");
        setProviderStatus(loadProviderStatus());
      }

      if (asset.status === "failed" && asset.error_message) {
        const msg = asset.error_message;
        if (NEEDS_UPGRADE_PATTERN.test(msg)) {
          toast.error(getDisplayErrorMessage(msg), {
            duration: Infinity,
            closeButton: true,
            action: { label: "Upgrade", onClick: () => router.push("/billing") },
          });
        } else {
          toast.error(getDisplayErrorMessage(msg));
        }
      }
    } catch (error) {
      const message = extractErrorMessage(error);
      updateMessage(assistantId, { status: "failed", errorMessage: message });
      if (NEEDS_UPGRADE_PATTERN.test(message)) {
        toast.error(getDisplayErrorMessage(message), {
          duration: Infinity,
          closeButton: true,
          action: { label: "Upgrade", onClick: () => router.push("/billing") },
        });
      } else {
        toast.error(getDisplayErrorMessage(message));
      }
    }
  }

  async function handleSubmit() {
    const typed = prompt.trim();
    const quoted = replyTo ? `> ${replyTo.replace(/\n/g, "\n> ")}\n\n` : "";
    const pasted = pastedBlock ? `\n\n${pastedBlock}` : "";
    const value = `${quoted}${typed}${pasted}`.trim();
    if (!value && attachments.length === 0) return;
    if (isSubmitting) return;

    const activeAttachments = attachments;
    setIsSubmitting(true);
    setPrompt("");
    setPastedBlock(null);
    setPastedBlockExpanded(false);
    setReplyTo(null);
    setAttachments([]);
    requestAnimationFrame(() => {
      if (textareaRef.current) textareaRef.current.style.height = `${MIN_TEXTAREA_HEIGHT}px`;
    });

    try {
      if (batchMode) {
        // Feature 6: fire off BATCH_COUNT variations in parallel so
        // the user can compare and pick the best result.
        const variationSuffixes = [
          "",
          " (give a different creative angle than usual)",
          " (try a distinct style/tone variation)",
        ];
        await Promise.all(
          Array.from({ length: BATCH_COUNT }, (_, i) =>
            submitPrompt(`${value}${variationSuffixes[i] ?? ""}`, i === 0 ? activeAttachments : undefined)
          )
        );
      } else {
        await submitPrompt(value, activeAttachments);
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  const STEP_LABELS: Record<string, string> = {
    research: "Researching",
    text: "Writing script",
    script: "Writing script",
    audio: "Generating voiceover",
    image: "Generating thumbnail",
    video: "Generating video",
    seo: "Writing SEO",
  };

  function pollWorkflow(workflowId: string, assistantId: string) {
    const poll = async () => {
      try {
        const { data: wf } = await apiClient.get<{
          status: string;
          steps: {
            asset_type: string;
            status: string;
            asset_id: string | null;
            error_message: string | null;
          }[];
        }>(`/api/v1/workflows/${workflowId}`);

        const running = wf.steps.find((s) => s.status === "running") ?? wf.steps.find((s) => s.status === "pending");

        if (wf.status === "completed" || wf.status === "failed" || wf.status === "completed_with_errors") {
          const textStep = wf.steps.find((s) => (s.asset_type === "text" || s.asset_type === "script") && s.asset_id);
          const videoStep = wf.steps.find((s) => s.asset_type === "video" && s.asset_id);
          const imageStep = wf.steps.find((s) => s.asset_type === "image" && s.asset_id);

          let finalText = "";
          let fileUrl: string | undefined;
          let assetType: string | undefined;

          if (videoStep?.asset_id) {
            const videoAsset = await getAsset(videoStep.asset_id);
            fileUrl = videoAsset.file_url ?? undefined;
            assetType = "video";
          } else if (imageStep?.asset_id) {
            const imageAsset = await getAsset(imageStep.asset_id);
            fileUrl = imageAsset.file_url ?? undefined;
            assetType = "image";
          }

          if (textStep?.asset_id) {
            const textAsset = await getAsset(textStep.asset_id);
            const meta = (textAsset.extra_metadata ?? {}) as Record<string, unknown>;
            finalText =
              (typeof meta.text === "string" && meta.text) ||
              (typeof meta.raw_result === "string" && meta.raw_result) ||
              "";
          }

          const failedSteps = wf.steps.filter((s) => s.status === "failed");
          const needsUpgrade = failedSteps.some((s) => NEEDS_UPGRADE_PATTERN.test(s.error_message || ""));
          const firstFailedError = failedSteps[0]?.error_message ?? null;

          if (failedSteps.length > 0) {
            finalText += (finalText ? "\n\n" : "") +
              failedSteps.map((s) => `${STEP_LABELS[s.asset_type] ?? s.asset_type} could not be completed.`).join("\n");
          }

          updateMessage(assistantId, {
            content: finalText || "Pipeline complete.",
            status: wf.status === "failed" ? "failed" : "completed",
            assetType,
            fileUrl,
            errorMessage: firstFailedError,
          });

          if (assetType) {
            recordProviderStatus(assetType, wf.status !== "failed");
            setProviderStatus(loadProviderStatus());
          }

          if (needsUpgrade) {
            toast.error(getDisplayErrorMessage(firstFailedError), {
              duration: Infinity,
              closeButton: true,
              action: { label: "Upgrade", onClick: () => router.push("/billing") },
            });
          } else if (wf.status === "failed") {
            toast.error(getDisplayErrorMessage(firstFailedError));
          } else if (wf.status === "completed_with_errors") {
            toast.error("Some steps didn't complete; the rest finished successfully.");
          } else {
            toast.success("Pipeline complete!");
          }

          return;
        }

        const label = running ? (STEP_LABELS[running.asset_type] ?? `${running.asset_type} generate ho raha hai`) : "Generating";
        updateMessage(assistantId, { status: "pending", content: `${label}...` });
        setTimeout(poll, 2000);
      } catch {
        setTimeout(poll, 3000);
      }
    };

    poll();
  }

  function handleNewChat() {
    clearMessages();
    clearStoredConversationId();
    setPrompt("");
    setAttachments([]);
    setPastedBlock(null);
    setPastedBlockExpanded(false);
    setReplyTo(null);
    toast.success("New chat started.");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  const waveColors = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"];

  return (
    <div className="flex h-full flex-col rounded-2xl border border-border bg-card shadow-sm">
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <span className="text-sm font-medium text-muted-foreground">Command Center</span>
        <div className="flex items-center gap-1">
          <a
            href="/assets"
            className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            title="View generated assets"
          >
            <Layers className="h-3.5 w-3.5" />
            Library
          </a>
          <button
            onClick={() => router.push("/billing")}
            className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-primary hover:bg-primary/10"
            title="Upgrade your plan"
          >
            <CreditCard className="h-3.5 w-3.5" />
            Upgrade
          </button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNewChat}
            className="gap-1.5 text-muted-foreground"
          >
            <Plus className="h-4 w-4" />
            New chat
          </Button>
        </div>
      </div>

      <ProviderStatusBar status={providerStatus} />

      <div
        ref={scrollRef}
        onMouseUp={handleBubbleMouseUp}
        className="flex-1 space-y-4 overflow-y-auto p-5"
      >
        {messages.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            Type a command below. Example: write a script about morning routines
          </div>
        ) : null}

        {messages.map((message) => {
          const isUser = message.role === "user";
          const isCardType = !isUser && message.assetType && CARD_ASSET_TYPES.has(message.assetType);
          const bubbleClass = isUser
            ? "max-w-[75%] space-y-2 rounded-2xl bg-chat-user px-4 py-3 text-[15px] leading-relaxed text-chat-user-foreground"
            : isCardType
            ? "max-w-[85%] w-full space-y-2"
            : "max-w-[75%] space-y-2 rounded-2xl bg-muted px-4 py-3 text-[15px] leading-relaxed text-foreground";
          const rowClass = isUser ? "flex flex-col items-end" : "flex flex-col items-start";

          return (
            <div key={message.id} className={rowClass}>
              <div className={bubbleClass}>
                {message.attachments?.length ? (
                  <div className="space-y-2">
                    {message.attachments.map((att) => (
                      <AttachmentPreview key={att.id} attachment={att} />
                    ))}
                  </div>
                ) : null}

                {message.status === "pending" ? (
                  <p className={isCardType ? "px-1 text-muted-foreground" : "text-muted-foreground"}>Generating...</p>
                ) : null}

                {message.status === "failed" ? (
                  <div className={isCardType ? "px-1" : ""}>
                    <p className="text-destructive">{getDisplayErrorMessage(message.errorMessage)}</p>
                    <button
                      onClick={() => handleRetry(message.id)}
                      className="mt-1 flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                    >
                      <RefreshCw className="h-3 w-3" />
                      Retry
                    </button>
                  </div>
                ) : null}

                {message.status === "completed" && message.content && isCardType ? (
                  <GeneratedContentCard
                    content={message.content}
                    assetType={message.assetType as string}
                    fileUrl={message.fileUrl}
                    onCopy={handleCopy}
                  />
                ) : message.status === "completed" && message.content ? (
                  renderContent(message.content, handleCopy, isUser)
                ) : null}

                {message.status === "completed" && message.fileUrl && message.assetType === "image" ? (
                  <img src={message.fileUrl} alt="Generated" className="max-h-64 rounded-lg border border-border object-cover" />
                ) : null}
                {message.status === "completed" && message.fileUrl && message.assetType === "video" ? (
                  <video src={message.fileUrl} controls className="max-h-64 w-full rounded-lg border border-border" />
                ) : null}
                {message.status === "completed" && message.fileUrl && message.assetType === "audio" ? (
                  <audio src={message.fileUrl} controls className="w-full" />
                ) : null}

                {message.status === "completed" && message.sources && message.sources.length > 0 && expandedSources.has(message.id) ? (
                  <div className="mt-2 space-y-1.5 rounded-lg border border-border bg-background/60 p-2.5">
                    <div className="mb-1 flex items-center gap-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                      <Link2 className="h-3 w-3" />
                      Sources
                    </div>
                    {message.sources.map((s, i) => (
                      <a
                        key={i}
                        href={s.url}
                        target="_blank"
                        rel="noreferrer"
                        className="block truncate text-xs text-primary hover:underline"
                        title={s.url}
                      >
                        {s.title || s.url}
                      </a>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="mt-1 flex items-center gap-3 px-1 text-xs font-medium text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 hover:!opacity-100">
                <button onClick={() => handleCopy(message.content)} className="flex items-center gap-1 hover:text-foreground">
                  <Copy className="h-3 w-3" />
                  Copy
                </button>
                {!isUser && message.sources && message.sources.length > 0 ? (
                  <button onClick={() => toggleSources(message.id)} className="flex items-center gap-1 hover:text-foreground">
                    <Link2 className="h-3 w-3" />
                    Sources ({message.sources.length})
                  </button>
                ) : null}
                {isUser ? (
                  <button onClick={() => handleEdit(message.content)} className="flex items-center gap-1 hover:text-foreground">
                    <Pencil className="h-3 w-3" />
                    Edit
                  </button>
                ) : null}
                <span>
                  {new Date(message.createdAt).toLocaleDateString([], { day: "2-digit", month: "short" })}{" "}
                  {new Date(message.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {selectionPopup ? (
        <button
          onClick={confirmReply}
          style={{ position: "fixed", left: selectionPopup.x, top: selectionPopup.y, transform: "translate(-50%, -100%)" }}
          className="z-50 flex items-center gap-1 rounded-lg bg-primary px-2.5 py-1.5 text-xs font-medium text-primary-foreground shadow-lg"
        >
          <CornerUpLeft className="h-3 w-3" />
          Reply
        </button>
      ) : null}

      <div className="relative border-t border-border p-3">
        {replyTo ? (
          <div className="mb-2 flex items-start gap-2 rounded-lg border border-border bg-muted px-3 py-2">
            <CornerUpLeft className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
            <p className="min-w-0 flex-1 truncate text-xs text-muted-foreground">{replyTo}</p>
            <button onClick={() => setReplyTo(null)} className="shrink-0 text-muted-foreground hover:text-destructive">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ) : null}

        {pastedBlock ? (
          <div className="mb-2 overflow-hidden rounded-lg border border-border bg-muted">
            <div className="flex items-center gap-2 px-3 py-2">
              <Paperclip className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
              <button
                type="button"
                onClick={() => setPastedBlockExpanded((v) => !v)}
                className="flex min-w-0 flex-1 items-center gap-2 text-left"
              >
                <span className="truncate text-xs text-muted-foreground">
                  {pastedBlockExpanded ? "Pasted text" : pastedBlock.slice(0, 60) + (pastedBlock.length > 60 ? "..." : "")}
                </span>
                <span className="shrink-0 rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-primary">
                  {pastedBlock.split("\n").length} lines
                </span>
                <ChevronDown className={`h-3.5 w-3.5 shrink-0 text-muted-foreground transition-transform ${pastedBlockExpanded ? "rotate-180" : ""}`} />
              </button>
              <button
                onClick={() => {
                  setPastedBlock(null);
                  setPastedBlockExpanded(false);
                }}
                className="shrink-0 text-muted-foreground hover:text-destructive"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            {pastedBlockExpanded ? (
              <textarea
                value={pastedBlock}
                onChange={(e) => setPastedBlock(e.target.value)}
                rows={12}
                className="max-h-64 w-full resize-none overflow-y-auto border-t border-border bg-background px-3 py-2 text-xs leading-relaxed focus-visible:outline-none"
              />
            ) : null}
          </div>
        ) : null}

        {attachments.length > 0 ? (
          <div className="mb-2 flex flex-wrap gap-2">
            {attachments.map((a) => (
              <div key={a.id} className="relative flex items-center gap-2 rounded-lg border border-border bg-muted px-2 py-1.5 text-xs">
                {a.kind === "image" ? (
                  <img src={a.url} alt={a.file.name} className="h-8 w-8 rounded object-cover" />
                ) : (
                  <FileText className="h-4 w-4" />
                )}
                <span className="max-w-[120px] truncate">{a.file.name}</span>
                <button onClick={() => removeAttachment(a.id)} className="text-muted-foreground hover:text-destructive">
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        ) : null}

        {toolsOpen ? (
          <div className="mb-2 max-h-64 overflow-y-auto rounded-lg border border-border bg-background p-2 shadow-sm">
            <div className="mb-2 flex items-center justify-between px-1">
              <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Prompt tools</span>
              <button onClick={() => setToolsOpen(false)} className="text-muted-foreground hover:text-destructive">
                <X className="h-3.5 w-3.5" />
              </button>
            </div>

            <label className="mb-2 flex items-center gap-1.5 rounded-md px-1.5 py-1 text-xs font-medium text-muted-foreground hover:bg-accent">
              <input
                type="checkbox"
                checked={batchMode}
                onChange={(e) => setBatchMode(e.target.checked)}
                className="h-3.5 w-3.5 rounded border-border"
              />
              Generate {BATCH_COUNT} variations
            </label>

            <button
              onClick={saveCurrentAsTemplate}
              className="mb-2 flex w-full items-center gap-1.5 rounded-md px-1.5 py-1 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              title="Save current prompt as a template"
            >
              <Star className="h-3.5 w-3.5" />
              Save current prompt as template
            </button>

            <div className="border-t border-border pt-2">
              <span className="mb-1 block px-1 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                Saved templates
              </span>
              {templates.length === 0 ? (
                <p className="px-1 py-1 text-xs text-muted-foreground">
                  No templates yet - type a prompt below, then tap "Save current prompt as template".
                </p>
              ) : (
                <div className="space-y-1">
                  {templates.map((t) => (
                    <div key={t.id} className="flex items-center gap-1 rounded-md px-1.5 py-1 hover:bg-accent">
                      <button onClick={() => useTemplate(t)} className="min-w-0 flex-1 truncate text-left text-xs text-foreground">
                        {t.label}
                      </button>
                      <button onClick={() => deleteTemplate(t.id)} className="shrink-0 text-muted-foreground hover:text-destructive">
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : null}

        <div className="relative flex flex-col gap-2 rounded-xl border border-border bg-background p-2 shadow-sm focus-within:ring-2 focus-within:ring-primary/20 transition-all">
          <div className="flex items-end gap-2">
            <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileSelect} />

            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 shrink-0 rounded-lg text-muted-foreground"
              onClick={() => setAttachMenuOpen((v) => !v)}
            >
              <Plus className={`h-5 w-5 transition-transform ${attachMenuOpen ? "rotate-45" : ""}`} />
            </Button>

            <div className="min-w-0 flex-1">
              <Textarea
                ref={textareaRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={handleKeyDown}
                onPaste={handlePaste}
                placeholder="Chat with CreatorOS. Ask for scripts, images, videos, or SEO content"
                className="w-full resize-none border-0 bg-transparent px-1 py-2.5 focus-visible:ring-0 min-h-[44px] max-h-[200px]"
              />
            </div>

            <div className="flex shrink-0 items-center gap-1 pr-1">
              {isRecording ? (
                <div className="mr-1 flex h-10 items-end gap-[3px]">
                  {waveLevels.map((level, i) => (
                    <span
                      key={i}
                      className="w-[3px] rounded-full transition-all duration-75"
                      style={{ height: `${level}px`, background: waveColors[i % waveColors.length] }}
                    />
                  ))}
                </div>
              ) : null}

              <Button
                variant="ghost"
                size="icon"
                onClick={() => setToolsOpen((v) => !v)}
                title="Templates and batch options"
                className={batchMode ? "text-primary" : undefined}
              >
                <Wand2 className="h-5 w-5" />
              </Button>

              <Button
                variant="ghost"
                size="icon"
                onClick={isRecording ? stopRecording : startRecording}
                title={isRecording ? "Stop recording" : "Record voice"}
              >
                {isRecording ? <Square className="h-4 w-4 fill-current" /> : <Mic className="h-5 w-5" />}
              </Button>

              <Button
                onClick={handleSubmit}
                disabled={isSubmitting || (!prompt.trim() && !pastedBlock && attachments.length === 0)}
                size="icon"
                className="h-9 w-9 rounded-lg shadow-sm"
              >
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>

        {attachMenuOpen ? (
          <div className="absolute bottom-full left-4 mb-2 w-48 rounded-xl border bg-popover p-1 shadow-xl z-50">
            <button onClick={() => openFilePicker("image/*")} className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-accent">
              <ImageIcon className="h-4 w-4 text-blue-500" /> Image
            </button>
            <button onClick={() => openFilePicker("video/*")} className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-accent">
              <Video className="h-4 w-4 text-purple-500" /> Video
            </button>
            <button onClick={() => openFilePicker("audio/*")} className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-accent">
              <Music className="h-4 w-4 text-pink-500" /> Audio
            </button>
            <button onClick={() => openFilePicker(".pdf,.doc,.docx,.txt,.csv,.xlsx")} className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-accent">
              <FileText className="h-4 w-4 text-orange-500" /> Document
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}

'@
[System.IO.File]::WriteAllText("C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\frontend\features\command-center\components\CommandInput.tsx", $cmdContent, (New-Object System.Text.UTF8Encoding($false)))
$assetsContent = @'
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ArrowLeft, Copy, Download, FileText, Loader2, RefreshCw } from "lucide-react";
import apiClient from "@/lib/api/client";

interface LibraryAsset {
  id: string;
  asset_type: string;
  status: string;
  prompt?: string | null;
  file_url?: string | null;
  extra_metadata?: Record<string, unknown> | null;
  created_at: string;
}

const TYPE_FILTERS = [
  { value: "", label: "All" },
  { value: "video", label: "Video" },
  { value: "image", label: "Image" },
  { value: "audio", label: "Audio" },
  { value: "text", label: "Script" },
  { value: "document", label: "Document" },
  { value: "seo", label: "SEO" },
];

function getAssetText(asset: LibraryAsset): string {
  const meta = asset.extra_metadata ?? {};
  const text = meta.text;
  const raw = meta.raw_result;
  if (typeof text === "string" && text) return text;
  if (typeof raw === "string" && raw) return raw;
  return "";
}

function AssetCard({ asset }: { asset: LibraryAsset }) {
  const text = getAssetText(asset);

  function handleCopy() {
    navigator.clipboard.writeText(text || asset.prompt || "");
    toast.success("Copied to clipboard.");
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
      <div className="border-b border-border bg-muted/40 px-3 py-2">
        <p className="truncate text-xs font-medium text-muted-foreground" title={asset.prompt ?? ""}>
          {asset.prompt || "Untitled"}
        </p>
      </div>

      <div className="p-3">
        {asset.asset_type === "image" && asset.file_url ? (
          <img src={asset.file_url} alt={asset.prompt ?? ""} className="mb-2 max-h-48 w-full rounded-lg object-cover" />
        ) : null}
        {asset.asset_type === "video" && asset.file_url ? (
          <video src={asset.file_url} controls className="mb-2 max-h-48 w-full rounded-lg" />
        ) : null}
        {asset.asset_type === "audio" && asset.file_url ? (
          <audio src={asset.file_url} controls className="mb-2 w-full" />
        ) : null}
        {(asset.asset_type === "text" || asset.asset_type === "document" || asset.asset_type === "seo" || asset.asset_type === "script") && text ? (
          <p className="mb-2 max-h-32 overflow-hidden whitespace-pre-wrap text-xs text-foreground/80">
            {text.slice(0, 300)}
            {text.length > 300 ? "..." : ""}
          </p>
        ) : null}

        {asset.status === "failed" ? (
          <p className="mb-2 text-xs text-destructive">Generation failed.</p>
        ) : null}

        <div className="flex items-center justify-between">
          <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            {asset.asset_type}
          </span>
          <div className="flex items-center gap-1">
            {text ? (
              <button onClick={handleCopy} className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground" title="Copy">
                <Copy className="h-3.5 w-3.5" />
              </button>
            ) : null}
            {asset.file_url ? (
              <a href={asset.file_url} download className="rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-accent-foreground" title="Download">
                <Download className="h-3.5 w-3.5" />
              </a>
            ) : null}
          </div>
        </div>
        <p className="mt-2 text-[10px] text-muted-foreground">
          {new Date(asset.created_at).toLocaleDateString([], { day: "2-digit", month: "short", year: "numeric" })}
        </p>
      </div>
    </div>
  );
}

export default function AssetsLibraryPage() {
  const router = useRouter();
  const [assets, setAssets] = useState<LibraryAsset[]>([]);
  const [typeFilter, setTypeFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadFailed, setLoadFailed] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 24;

  async function loadAssets(reset: boolean) {
    setLoading(true);
    setLoadFailed(false);
    try {
      const nextOffset = reset ? 0 : offset;
      const { data } = await apiClient.get<LibraryAsset[]>("/api/v1/assets", {
        params: {
          asset_type: typeFilter || undefined,
          limit: LIMIT,
          offset: nextOffset,
        },
      });
      setAssets((prev) => (reset ? data : [...prev, ...data]));
      setOffset(nextOffset + data.length);
      setHasMore(data.length === LIMIT);
    } catch {
      setLoadFailed(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAssets(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [typeFilter]);

  return (
    <div className="mx-auto max-w-5xl p-6">
      <div className="mb-4 flex items-center gap-3">
        <button
          onClick={() => router.back()}
          title="Back"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Asset Library</h1>
          <p className="mt-1 text-sm text-muted-foreground">Everything you've generated - scripts, images, videos, audio, and more.</p>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-1.5">
        {TYPE_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setTypeFilter(f.value)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              typeFilter === f.value
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loadFailed ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center">
          <p className="mb-2 text-sm text-muted-foreground">Could not load your assets right now.</p>
          <button
            onClick={() => loadAssets(true)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-accent"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Try again
          </button>
        </div>
      ) : loading && assets.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
        </div>
      ) : assets.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
          <FileText className="mx-auto mb-2 h-6 w-6" />
          Nothing here yet. Generate something in Command Center and it'll show up here.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {assets.map((a) => (
              <AssetCard key={a.id} asset={a} />
            ))}
          </div>
          {hasMore ? (
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => loadAssets(false)}
                disabled={loading}
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-accent disabled:opacity-50"
              >
                {loading ? "Loading..." : "Load more"}
              </button>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}

'@
[System.IO.File]::WriteAllText("C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\frontend\app\assets\page.tsx", $assetsContent, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Both files written: CommandInput.tsx (toolbar redesign + upgrade button) and app/assets/page.tsx (library page)." -ForegroundColor Green
