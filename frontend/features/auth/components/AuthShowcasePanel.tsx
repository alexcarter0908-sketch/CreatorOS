"use client";

import { useEffect, useState } from "react";
import { Check, FileText, Image as ImageIcon, Loader2, Search, Video, Zap } from "lucide-react";

type Variant = "login" | "register";

const COPY: Record<Variant, { eyebrow: string; headline: string; tagline: string; command: string }> = {
  login: {
    eyebrow: "Welcome back",
    headline: "Your AI-powered creator operating system",
    tagline: "Sign in and pick up right where the last upload left off.",
    command: "Make a video about the top 5 AI editing tools",
  },
  register: {
    eyebrow: "Start creating",
    headline: "Your AI-powered creator operating system",
    tagline: "Create an account and let the command center handle the busywork.",
    command: "Write a script for my next upload",
  },
};

const PIPELINE_STEPS = [
  { label: "Script generated", icon: FileText },
  { label: "Thumbnail rendered", icon: ImageIcon },
  { label: "Video assembled", icon: Video },
  { label: "SEO tags ready", icon: Search },
];

const FEATURES = [
  { label: "Scripts written for you", icon: FileText },
  { label: "Thumbnails generated instantly", icon: ImageIcon },
  { label: "Videos assembled automatically", icon: Video },
  { label: "SEO tags optimized", icon: Search },
  { label: "Automation runs on schedule", icon: Zap },
];

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default function AuthShowcasePanel({ variant }: { variant: Variant }) {
  const copy = COPY[variant];

  const [typed, setTyped] = useState("");
  const [activeStep, setActiveStep] = useState(-1);
  const [completedSteps, setCompletedSteps] = useState<boolean[]>(() => PIPELINE_STEPS.map(() => false));
  const [featuresVisible, setFeaturesVisible] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      // reset for this mount
      setTyped("");
      setActiveStep(-1);
      setCompletedSteps(PIPELINE_STEPS.map(() => false));
      setFeaturesVisible(false);

      await sleep(400);

      for (let i = 1; i <= copy.command.length; i++) {
        if (cancelled) return;
        setTyped(copy.command.slice(0, i));
        await sleep(28);
      }

      await sleep(500);

      for (let i = 0; i < PIPELINE_STEPS.length; i++) {
        if (cancelled) return;
        setActiveStep(i);
        await sleep(650);
        if (cancelled) return;
        setCompletedSteps((prev) => prev.map((done, idx) => (idx === i ? true : done)));
        await sleep(150);
      }

      await sleep(300);
      if (!cancelled) setFeaturesVisible(true);
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [variant, copy.command]);

  return (
    <div
      className="relative hidden w-full flex-col justify-center gap-10 overflow-hidden px-14 py-16 text-white lg:flex lg:flex-1"
      style={{
        background:
          "radial-gradient(1100px circle at 12% -10%, rgba(124,110,231,0.35), transparent 55%), radial-gradient(900px circle at 100% 105%, rgba(16,45,101,0.45), transparent 60%), #07040c",
      }}
    >
      <div className="flex items-center gap-2.5">
        <img src="/logo.png" alt="CreatorOS" className="h-8 w-8 rounded-lg object-cover" />
        <span className="text-sm font-semibold tracking-wide text-white/90">CreatorOS</span>
      </div>

      <div className="max-w-md space-y-3">
        <p className="text-xs font-medium uppercase tracking-widest text-violet-300/80">{copy.eyebrow}</p>
        <h2 className="text-[26px] font-semibold leading-tight text-white">{copy.headline}</h2>
        <p className="text-sm text-white/60">{copy.tagline}</p>
      </div>

      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-white/[0.04] p-5 shadow-[0_0_0_1px_rgba(255,255,255,0.02)]">
        <p className="mb-3 text-[11px] font-medium uppercase tracking-widest text-white/40">Command center</p>

        <div className="mb-4 rounded-xl border border-white/10 bg-black/30 px-4 py-3 font-mono text-[13px] text-white/90">
          {typed}
          <span className="ml-0.5 inline-block h-3.5 w-[2px] animate-pulse bg-violet-300 align-middle" />
        </div>

        <div className="space-y-2.5">
          {PIPELINE_STEPS.map((step, i) => {
            const started = activeStep >= i;
            if (!started) return null;
            const done = completedSteps[i];
            const Icon = step.icon;
            return (
              <div key={step.label} className="flex items-center gap-2.5 text-[13px] text-white/80">
                {done ? (
                  <Check className="h-4 w-4 shrink-0 text-emerald-400" />
                ) : (
                  <Loader2 className="h-4 w-4 shrink-0 animate-spin text-violet-300" />
                )}
                <Icon className="h-3.5 w-3.5 shrink-0 text-white/40" />
                <span>{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="w-full max-w-md space-y-3">
        {FEATURES.map((feature, i) => {
          const Icon = feature.icon;
          return (
            <div
              key={feature.label}
              className="flex items-center gap-3 transition-all duration-500 ease-out"
              style={{
                opacity: featuresVisible ? 1 : 0,
                transform: featuresVisible ? "translateY(0)" : "translateY(8px)",
                transitionDelay: `${i * 90}ms`,
              }}
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/[0.06]">
                <Icon className="h-4 w-4 text-violet-300" />
              </div>
              <span className="text-[13px] text-white/75">{feature.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}