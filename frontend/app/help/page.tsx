import MainLayout from "@/components/layout/MainLayout";
import { Terminal, Zap, FolderKanban, Mail } from "lucide-react";

const FAQS = [
  {
    icon: Terminal,
    question: "How do I generate content?",
    answer:
      "Go to the Command Center and type any request in plain English, like write a script for my next video. CreatorOS routes it to the right AI agent automatically.",
  },
  {
    icon: Zap,
    question: "What is Automation?",
    answer:
      "Automation lets you set a recurring target, such as one image every day, and CreatorOS generates it for you in the background with no manual command needed.",
  },
  {
    icon: FolderKanban,
    question: "How do Projects work?",
    answer:
      "Projects group related content together. Create a project, then tag your commands and assets to it to keep everything organized.",
  },
  {
    icon: Terminal,
    question: "Why did my generation fail?",
    answer:
      "Generation can fail if the connected AI provider has no valid API key or is temporarily unavailable. Check Scripts, Videos, or Thumbnails for the specific error message.",
  },
];

export default function HelpPage() {
  return (
    <MainLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Help and Support</h1>
        <p className="mt-2 text-muted-foreground">Everything you need to know about CreatorOS.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {FAQS.map((faq) => {
          const Icon = faq.icon;
          return (
            <div key={faq.question} className="rounded-2xl border bg-card p-6 shadow-sm">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
                <Icon className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="mb-2 font-semibold text-foreground">{faq.question}</h3>
              <p className="text-sm text-muted-foreground">{faq.answer}</p>
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex items-center gap-4 rounded-2xl border bg-slate-900 p-6 text-white">
        <Mail className="h-6 w-6 shrink-0" />
        <div>
          <p className="font-semibold">Still need help?</p>
          <p className="text-sm text-slate-300">Reach out to your workspace administrator.</p>
        </div>
      </div>
    </MainLayout>
  );
}
