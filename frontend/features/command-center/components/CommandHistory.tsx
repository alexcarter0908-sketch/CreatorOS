"use client";
import { useCommandStore } from "../store/command.store";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function CommandHistory() {
  const messages = useCommandStore((state) => state.messages);

  if (messages.length === 0) {
    return (
      <div className="rounded-xl border border-dashed p-6 text-center text-sm text-muted-foreground">
        No commands yet.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {messages
        .slice()
        .reverse()
        .map((message) => (
          <div key={message.id} className="group/msg rounded-xl border p-4">
            <div className="font-medium text-sm leading-relaxed space-y-2 [&_h1]:text-lg [&_h1]:font-bold [&_h1]:mt-3 [&_h1]:mb-1 [&_h2]:text-base [&_h2]:font-bold [&_h2]:mt-3 [&_h2]:mb-1 [&_h3]:text-sm [&_h3]:font-semibold [&_h3]:mt-2 [&_h3]:mb-1 [&_p]:mb-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:mb-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:mb-2 [&_li]:mb-1 [&_strong]:font-semibold [&_blockquote]:border-l-4 [&_blockquote]:border-primary [&_blockquote]:bg-muted [&_blockquote]:rounded-md [&_blockquote]:px-3 [&_blockquote]:py-2 [&_blockquote]:my-2 [&_code]:bg-muted [&_code]:rounded [&_code]:px-1 [&_code]:py-0.5 [&_code]:text-xs">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
            <div className="mt-2 flex items-center justify-between text-sm text-muted-foreground">
              <span>{message.status}</span>
              <span className="opacity-0 transition-opacity duration-150 group-hover/msg:opacity-100">
                {new Date(message.createdAt).toLocaleDateString([], { day: "2-digit", month: "short" })}{" "}
                {new Date(message.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        ))}
    </div>
  );
}