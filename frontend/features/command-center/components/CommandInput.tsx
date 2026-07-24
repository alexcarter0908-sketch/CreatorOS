"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
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
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import apiClient from "@/lib/api/client";
import { useCommandStore } from "../store/command.store";
import { runCommand } from "../services/command.service";
import { fetchConversation } from "../services/conversation.service";
import { getStoredConversationId } from "../services/command.service";
import { getAsset } from "@/features/assets/services/asset.service";
import type { ChatMessage, ChatAttachment, AttachmentKind } from "../types/command";
import type { AICommandHistoryTurn } from "@/lib/ai/gateway";
import { clearStoredConversationId } from "../services/command.service";

const MIN_TEXTAREA_HEIGHT = 44;
const MAX_TEXTAREA_HEIGHT = 200;
const PASTE_LINE_THRESHOLD = 500;
const COLLAPSE_LENGTH = 500;
const COLLAPSE_LINES = 500;
const WAVE_BAR_COUNT = 28;

function extractErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

function buildHistory(messages: ChatMessage[]): AICommandHistoryTurn[] {
  return messages
    .filter((m) => m.status === "completed" && m.content.trim().length > 0)
    .slice(-6)
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

/* ---------- Inline **bold** support ---------- */
function renderInline(text: string, keyPrefix: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? (
      <strong key={`${keyPrefix}-b-${i}`} className="font-bold text-foreground">
        {p.slice(2, -2)}
      </strong>
    ) : (
      <span key={`${keyPrefix}-t-${i}`}>{p}</span>
    )
  );
}

const LABEL_PATTERN = /^([A-Za-z][A-Za-z \-]{1,28}):\s*(.*)$/;

/* ---------- Renders one line: headings / labels (Scene, Visual, VO...) / bullets / text ---------- */
function renderLine(line: string, key: string) {
  const h3 = line.match(/^###\s+(.*)$/);
  if (h3) {
    return (
      <h4 key={key} className="mt-3 mb-1 text-[11px] font-bold uppercase tracking-wider text-primary">
        {h3[1]}
      </h4>
    );
  }
  const h2 = line.match(/^##\s+(.*)$/);
  if (h2) {
    return (
      <h3 key={key} className="mt-4 mb-1.5 text-[15px] font-extrabold text-foreground">
        {h2[1]}
      </h3>
    );
  }
  const h1 = line.match(/^#\s+(.*)$/);
  if (h1) {
    return (
      <h2 key={key} className="mt-4 mb-1.5 text-base font-extrabold text-foreground">
        {h1[1]}
      </h2>
    );
  }
  const bullet = line.match(/^[*-]\s+(.*)$/);
  if (bullet) {
    return (
      <li key={key} className="ml-4 list-disc leading-relaxed">
        {renderInline(bullet[1], key)}
      </li>
    );
  }
  const label = line.match(LABEL_PATTERN);
  if (label && label[1].split(" ").length <= 4) {
    return (
      <p key={key} className="leading-relaxed">
        <strong className="font-bold text-foreground">{label[1]}:</strong> {renderInline(label[2], key)}
      </p>
    );
  }
  if (!line.trim()) return null;
  return (
    <p key={key} className="whitespace-pre-wrap leading-relaxed">
      {renderInline(line, key)}
    </p>
  );
}

function TextLines({ text }: { text: string }) {
  return <div className="space-y-1">{text.split("\n").map((l, i) => renderLine(l, `l-${i}`))}</div>;
}

/* ---------- Boxed document (script/command) with its own Copy/Download ---------- */
function isStructuredDocument(text: string) {
  const h1h2 = text.match(/^#{1,2}\s+.+$/gm) || [];
  const h3 = text.match(/^#{3}\s+.+$/gm) || [];
  return h1h2.length >= 1 && h3.length >= 2;
}

function StructuredDocumentBlock({ text, onCopy }: { text: string; onCopy: (t: string) => void }) {
  function handleDownload() {
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "script.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="my-2 overflow-hidden rounded-xl border border-border bg-background shadow-sm">
      <div className="flex items-center justify-between border-b border-border bg-muted/60 px-3 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Document</span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onCopy(text)}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            title="Copy"
          >
            <Copy className="h-3.5 w-3.5" />
            Copy
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            title="Download"
          >
            <Download className="h-3.5 w-3.5" />
            Download
          </button>
        </div>
      </div>
      <div className="max-h-[420px] overflow-y-auto px-4 py-3 text-[15px]">
        <TextLines text={text} />
      </div>
    </div>
  );
}

/* ---------- Collapsible long text ---------- */
function CollapsibleText({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const lineCount = text.split("\n").length;
  const isLong = lineCount > COLLAPSE_LINES;

  if (!isLong) {
    return <TextLines text={text} />;
  }

  return (
    <div className="my-1 overflow-hidden rounded-lg border border-border bg-muted/50">
      <div className={`p-3 text-sm ${expanded ? "" : "max-h-32 overflow-hidden"}`}>
        <TextLines text={text} />
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

function extractSourcesSection(text: string) {
  const lines = text.split("\n");
  const headingRe = /^(#{1,3}\s*)?(official\s+)?sources\s*:?\s*$/i;
  let idx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (headingRe.test(lines[i].trim())) {
      idx = i;
      break;
    }
  }
  if (idx === -1) return { mainText: text, links: [] as { title: string; url: string }[] };

  const before = lines.slice(0, idx).join("\n").trim();
  const after = lines.slice(idx + 1);
  const links: { title: string; url: string }[] = [];
  const leftover: string[] = [];
  const linkPattern = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/;

  for (const line of after) {
    const m = line.match(linkPattern);
    if (m) {
      links.push({ title: m[1], url: m[2] });
    } else if (line.trim()) {
      leftover.push(line.replace(/^[*-]\s*/, ""));
    }
  }

  const mainText = [before, ...leftover].filter(Boolean).join("\n\n");
  return { mainText, links };
}

function SourcesRow({ links }: { links: { title: string; url: string }[] }) {
  if (links.length === 0) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {links.map((l, i) => (
        <a
          key={i}
          href={l.url}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 rounded-full border border-border bg-background px-2.5 py-1 text-[11px] text-muted-foreground hover:bg-accent hover:text-foreground"
          title={l.url}
        >
          <Link2 className="h-3 w-3" />
          <span className="max-w-[140px] truncate">{l.title}</span>
        </a>
      ))}
    </div>
  );
}

function renderContent(content: string, onCopy: (t: string) => void, collapsible: boolean) {
  const { mainText, links } = extractSourcesSection(content);
  const segments = parseSegments(mainText).map((seg, i) => {
    if (seg.type === "code") {
      return <CodeBlock key={i} code={seg.content} lang={seg.lang} onCopy={onCopy} />;
    }
    if (isStructuredDocument(seg.content)) {
      return <StructuredDocumentBlock key={i} text={seg.content} onCopy={onCopy} />;
    }
    return collapsible ? <CollapsibleText key={i} text={seg.content} /> : <TextLines key={i} text={seg.content} />;
  });
  return (
    <>
      {segments}
      <SourcesRow links={links} />
    </>
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
    <a
      href={attachment.url}
      target="_blank"
      rel="noreferrer"
      className="flex items-center gap-2 rounded-lg border border-border bg-muted px-3 py-2 text-sm hover:bg-accent"
    >
      <FileText className="h-4 w-4 shrink-0" />
      <span className="truncate">{attachment.name}</span>
    </a>
  );
}

export default function CommandInput() {
  const searchParams = useSearchParams();
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
        if (msgs.length > 0) setMessages(msgs);
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
      analyser.fftSize = 128;
      source.connect(analyser);
      audioContextRef.current = audioContext;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      function updateLevels() {
        analyser.getByteTimeDomainData(dataArray);
        const chunkSize = Math.max(1, Math.floor(dataArray.length / WAVE_BAR_COUNT));
        const levels = Array.from({ length: WAVE_BAR_COUNT }, (_, i) => {
          const start = i * chunkSize;
          let maxDev = 0;
          for (let j = start; j < start + chunkSize && j < dataArray.length; j++) {
            maxDev = Math.max(maxDev, Math.abs(dataArray[j] - 128));
          }
          const normalized = maxDev / 128;
          const boosted = Math.pow(normalized, 0.5); // amplify quiet/normal speech
          return Math.max(3, Math.min(32, boosted * 32));
        });
        setWaveLevels(levels);
        animationFrameRef.current = requestAnimationFrame(updateLevels);
      }
      updateLevels();

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const file = new File([blob], `voice-${Date.now()}.webm`, { type: "audio/webm" });
        const url = URL.createObjectURL(file);
        setAttachments((prev) => [...prev, { id: crypto.randomUUID(), file, url, kind: "audio" }]);
        stream.getTracks().forEach((t) => t.stop());
        if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
        audioContext.close();
        setWaveLevels(Array(WAVE_BAR_COUNT).fill(3));
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

  async function handleSubmit() {
    const typed = prompt.trim();
    const quoted = replyTo ? `> ${replyTo.replace(/\n/g, "\n> ")}\n\n` : "";
    const pasted = pastedBlock ? `\n\n${pastedBlock}` : "";
    const value = `${quoted}${typed}${pasted}`.trim();
    if (!value && attachments.length === 0) return;
    if (isSubmitting) return;

    const history = buildHistory(messages);
    const chatAttachments: ChatAttachment[] | undefined =
      attachments.length > 0
        ? attachments.map((a) => ({ id: a.id, url: a.url, kind: a.kind, name: a.file.name }))
        : undefined;

    setIsSubmitting(true);
    setPrompt("");
    setPastedBlock(null);
    setPastedBlockExpanded(false);
    setReplyTo(null);
    setAttachments([]);
    requestAnimationFrame(() => {
      if (textareaRef.current) textareaRef.current.style.height = `${MIN_TEXTAREA_HEIGHT}px`;
    });

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
      // Backend may save the reply under different keys depending on
      // which agent handled it (text / raw_result / result) - check
      // all of them instead of assuming "text", or the message shows
      // as an empty bubble even though the backend succeeded.
      const text =
        (typeof meta.text === "string" && meta.text) ||
        (typeof meta.raw_result === "string" && meta.raw_result) ||
        (typeof meta.result === "string" && meta.result) ||
        "";

      updateMessage(assistantId, {
        content: text,
        status: asset.status === "failed" ? "failed" : "completed",
        assetType: asset.asset_type,
        fileUrl: asset.file_url,
        errorMessage: asset.error_message,
      });

      if (asset.status === "failed" && asset.error_message) {
        toast.error(asset.error_message);
      }
      setIsSubmitting(false);
    } catch (error) {
      const message = extractErrorMessage(error);
      updateMessage(assistantId, { status: "failed", errorMessage: message });
      toast.error(message);
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
          if (failedSteps.length > 0) {
            finalText += (finalText ? "\n\n" : "") +
              failedSteps.map((s) => `${STEP_LABELS[s.asset_type] ?? s.asset_type} failed: ${s.error_message ?? "unknown error"}`).join("\n");
          }

          updateMessage(assistantId, {
            content: finalText || "Pipeline complete.",
            status: wf.status === "failed" ? "failed" : "completed",
            assetType,
            fileUrl,
          });

          if (wf.status === "failed") {
            toast.error("Pipeline failed.");
          } else if (wf.status === "completed_with_errors") {
            toast.error("Some steps failed; the rest completed.");
          } else {
            toast.success("Pipeline complete!");
          }

          setIsSubmitting(false);
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
          const bubbleClass = isUser
            ? "max-w-[75%] space-y-2 rounded-2xl bg-chat-user px-4 py-3 text-[15px] leading-relaxed text-chat-user-foreground"
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
                  <p className="text-muted-foreground">Generating...</p>
                ) : null}

                {message.status === "failed" ? (
                  <p className="text-destructive">{message.errorMessage ?? "Something went wrong."}</p>
                ) : null}

                {message.status === "completed" && message.content ? renderContent(message.content, handleCopy, isUser) : null}

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
                <div className="mr-1 flex h-6 items-end gap-[2px]">
                  {waveLevels.map((level, i) => (
                    <span
                      key={i}
                      className="w-[2px] rounded-full transition-all duration-75"
                      style={{ height: `${level}px`, background: waveColors[i % waveColors.length] }}
                    />
                  ))}
                </div>
              ) : null}

              <Button
                variant="ghost"
                size="icon"
                className={`h-9 w-9 rounded-lg transition-colors ${isRecording ? "bg-destructive/10 text-destructive animate-pulse" : "text-muted-foreground"}`}
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

        {attachMenuOpen && (
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
        )}
      </div>
    </div>
  );
}
