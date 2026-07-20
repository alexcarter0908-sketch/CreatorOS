"use client";

// Save & reuse frequently-used prompts (e.g. "YouTube Shorts script about
// [topic]") with one click. Stored in localStorage for now - swap the
// load/save/delete bodies below for API calls (e.g. GET/POST/DELETE
// /api/v1/prompt-templates) if you want templates synced across devices.
//
// Usage inside CommandInput.tsx:
//   const { templates, saveTemplate, deleteTemplate } = usePromptTemplates();
//   <PromptTemplatesMenu
//     templates={templates}
//     currentPrompt={prompt}
//     onUse={(text) => setPrompt(text)}
//     onSave={saveTemplate}
//     onDelete={deleteTemplate}
//   />
// Render <PromptTemplatesMenu /> as one more icon button next to the
// attach ("+") button in the composer row.

import { useEffect, useState } from "react";
import { BookMarked, Plus, Trash2, X } from "lucide-react";

const STORAGE_KEY = "creatoros:prompt-templates";

export interface PromptTemplate {
  id: string;
  label: string;
  text: string;
  createdAt: string;
}

function loadTemplates(): PromptTemplate[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as PromptTemplate[]) : [];
  } catch {
    return [];
  }
}

function persistTemplates(templates: PromptTemplate[]) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
  } catch {
    // ignore (private browsing / storage full)
  }
}

export function usePromptTemplates() {
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);

  useEffect(() => {
    setTemplates(loadTemplates());
  }, []);

  function saveTemplate(label: string, text: string) {
    const next: PromptTemplate = {
      id: crypto.randomUUID(),
      label: label.trim() || text.slice(0, 40),
      text,
      createdAt: new Date().toISOString(),
    };
    setTemplates((prev) => {
      const updated = [next, ...prev];
      persistTemplates(updated);
      return updated;
    });
  }

  function deleteTemplate(id: string) {
    setTemplates((prev) => {
      const updated = prev.filter((t) => t.id !== id);
      persistTemplates(updated);
      return updated;
    });
  }

  return { templates, saveTemplate, deleteTemplate };
}

export function PromptTemplatesMenu({
  templates,
  currentPrompt,
  onUse,
  onSave,
  onDelete,
}: {
  templates: PromptTemplate[];
  currentPrompt: string;
  onUse: (text: string) => void;
  onSave: (label: string, text: string) => void;
  onDelete: (id: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [savingLabel, setSavingLabel] = useState("");
  const [showSaveInput, setShowSaveInput] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent"
        title="Prompt templates"
      >
        <BookMarked className="h-4.5 w-4.5" />
      </button>

      {open ? (
        <div className="absolute bottom-full left-0 z-50 mb-2 w-72 rounded-xl border bg-popover p-2 shadow-xl">
          <div className="mb-1 flex items-center justify-between px-1">
            <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Prompt templates</span>
            <button onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>

          {currentPrompt.trim() ? (
            showSaveInput ? (
              <div className="mb-2 flex items-center gap-1 px-1">
                <input
                  autoFocus
                  value={savingLabel}
                  onChange={(e) => setSavingLabel(e.target.value)}
                  placeholder="Template name"
                  className="min-w-0 flex-1 rounded-md border border-border bg-background px-2 py-1 text-xs outline-none"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      onSave(savingLabel, currentPrompt);
                      setSavingLabel("");
                      setShowSaveInput(false);
                    }
                  }}
                />
                <button
                  onClick={() => {
                    onSave(savingLabel, currentPrompt);
                    setSavingLabel("");
                    setShowSaveInput(false);
                  }}
                  className="rounded-md bg-primary px-2 py-1 text-xs font-medium text-primary-foreground"
                >
                  Save
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowSaveInput(true)}
                className="mb-2 flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-xs font-medium text-primary hover:bg-accent"
              >
                <Plus className="h-3.5 w-3.5" />
                Save current prompt as template
              </button>
            )
          ) : null}

          {templates.length === 0 ? (
            <p className="px-1 py-2 text-xs text-muted-foreground">No saved templates yet.</p>
          ) : (
            <div className="max-h-64 space-y-0.5 overflow-y-auto">
              {templates.map((t) => (
                <div key={t.id} className="group flex items-center gap-1 rounded-lg px-2 py-1.5 hover:bg-accent">
                  <button
                    onClick={() => {
                      onUse(t.text);
                      setOpen(false);
                    }}
                    className="min-w-0 flex-1 text-left"
                    title={t.text}
                  >
                    <p className="truncate text-xs font-medium text-foreground">{t.label}</p>
                    <p className="truncate text-[11px] text-muted-foreground">{t.text}</p>
                  </button>
                  <button
                    onClick={() => onDelete(t.id)}
                    className="shrink-0 text-muted-foreground opacity-0 hover:text-destructive group-hover:opacity-100"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
