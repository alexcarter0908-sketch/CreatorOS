"use client";

import { useEffect, useState } from "react";
import { Check, FileText, Image as ImageIcon, Loader2, Mic, Palette, Scissors, Search, Sparkles, Tag, Video, Wand2 } from "lucide-react";

type Variant = "login" | "register";

const COPY: Record<Variant, { eyebrow: string; headline: string; tagline: string; command: string; clip: string }> = {
  login: {
    eyebrow: "Welcome back",
    headline: "Your AI-powered creator operating system",
    tagline: "Sign in and pick up right where the last upload left off.",
    command: "Make a video about the top 5 AI editing tools",
    clip: "Top 5 AI editing tools",
  },
  register: {
    eyebrow: "Start creating",
    headline: "Your AI-powered creator operating system",
    tagline: "Create an account and let the command center handle the busywork.",
    command: "Write a script for my next upload",
    clip: "Your next upload",
  },
};

const PIPELINE_STEPS = [
  { label: "Searching topic", icon: Search },
  { label: "Writing script", icon: FileText },
  { label: "Generating thumbnail", icon: ImageIcon },
  { label: "Optimizing SEO", icon: Tag },
  { label: "Generating video", icon: Video },
];

const CLIP_HIGHLIGHTS = [
  { label: "Auto captions", icon: FileText },
  { label: "Voice cloning", icon: Mic },
  { label: "Smart cut", icon: Scissors },
  { label: "Color grade", icon: Palette },
  { label: "AI enhance", icon: Wand2 },
];

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default function AuthShowcasePanel({ variant }: { variant: Variant }) {
  const copy = COPY[variant];

  const [typed, setTyped] = useState("");
  const [activeStep, setActiveStep] = useState(-1);
  const [completedSteps, setCompletedSteps] = useState<boolean[]>(() => PIPELINE_STEPS.map(() => false));
  const [videoReady, setVideoReady] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [scene, setScene] = useState<"logo" | "title" | "highlights">("logo");
  const [highlightIndex, setHighlightIndex] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      setTyped("");
      setActiveStep(-1);
      setCompletedSteps(PIPELINE_STEPS.map(() => false));
      setVideoReady(false);
      setVideoProgress(0);
      setScene("logo");
      setHighlightIndex(0);

      await sleep(400);

      for (let i = 1; i <= copy.command.length; i++) {
        if (cancelled) return;
        setTyped(copy.command.slice(0, i));
        await sleep(26);
      }

      await sleep(450);

      for (let i = 0; i < PIPELINE_STEPS.length; i++) {
        if (cancelled) return;
        setActiveStep(i);
        await sleep(520);
        if (cancelled) return;
        setCompletedSteps((prev) => prev.map((done, idx) => (idx === i ? true : done)));
        await sleep(120);
      }

      await sleep(300);
      if (!cancelled) setVideoReady(true);
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [variant, copy.command]);

  useEffect(() => {
    if (!videoReady) return;
    const id = setInterval(() => {
      setVideoProgress((p) => (p >= 100 ? 0 : p + 2));
    }, 120);
    return () => clearInterval(id);
  }, [videoReady]);

  useEffect(() => {
    if (!videoReady) return;
    let cancelled = false;

    async function loop() {
      while (!cancelled) {
        setScene("logo");
        await sleep(1400);
        if (cancelled) return;

        setScene("title");
        await sleep(1400);
        if (cancelled) return;

        setScene("highlights");
        for (let i = 0; i < CLIP_HIGHLIGHTS.length; i++) {
          if (cancelled) return;
          setHighlightIndex(i);
          await sleep(1500);
        }
      }
    }

    loop();
    return () => {
      cancelled = true;
    };
  }, [videoReady]);

  return (
    <div
      className="relative hidden h-screen w-full flex-col overflow-hidden px-12 py-10 text-white lg:flex lg:flex-1 xl:px-16"
      style={{
        background:
          "radial-gradient(1100px circle at 12% -10%, rgba(124,110,231,0.35), transparent 55%), radial-gradient(900px circle at 100% 105%, rgba(16,45,101,0.45), transparent 60%), #07040c",
      }}
    >
      <img
        src="/logo.png"
        alt=""
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 m-auto h-[620px] w-[620px] object-contain opacity-[0.16]"
      />

      <div className="relative z-10 flex h-full flex-col justify-center gap-7">
        <div className="flex items-center gap-3">
          <img src="/logo-icon.png" alt="Synapse-X-CreatorOS" className="h-14 w-14 rounded-xl object-cover" />
          <span className="text-xl font-semibold tracking-wide text-white">Synapse-X-CreatorOS</span>
        </div>

        <div className="max-w-md space-y-2.5">
          <p className="text-xs font-medium uppercase tracking-widest text-violet-300/80">{copy.eyebrow}</p>
          <h2 className="text-[24px] font-semibold leading-tight text-white">{copy.headline}</h2>
          <p className="text-sm text-white/60">{copy.tagline}</p>
        </div>

        <div className="w-full max-w-md rounded-2xl border border-white/10 bg-white/[0.04] p-4">
          <p className="mb-2.5 text-[11px] font-medium uppercase tracking-widest text-white/40">Command center</p>

          <div className="mb-3 rounded-xl border border-white/10 bg-black/30 px-4 py-2.5 font-mono text-[13px] text-white/90">
            {typed}
            <span className="ml-0.5 inline-block h-3.5 w-[2px] animate-pulse bg-violet-300 align-middle" />
          </div>

          <div className="space-y-2">
            {PIPELINE_STEPS.map((step, i) => {
              const started = activeStep >= i;
              if (!started) return null;
              const done = completedSteps[i];
              const Icon = step.icon;
              return (
                <div key={step.label} className="flex items-center gap-2.5 text-[12.5px] text-white/80">
                  {done ? (
                    <Check className="h-3.5 w-3.5 shrink-0 text-emerald-400" />
                  ) : (
                    <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin text-violet-300" />
                  )}
                  <Icon className="h-3.5 w-3.5 shrink-0 text-white/40" />
                  <span>{step.label}</span>
                </div>
              );
            })}
          </div>

          <div
            className="overflow-hidden transition-all duration-500 ease-out"
            style={{
              maxHeight: videoReady ? "150px" : "0px",
              opacity: videoReady ? 1 : 0,
              marginTop: videoReady ? "14px" : "0px",
            }}
          >
            <div className="relative h-[128px] w-full overflow-hidden rounded-lg border border-white/10 bg-gradient-to-br from-[#241d3a] via-[#2c1f45] to-[#151225]">
              <div
                className="absolute -inset-y-10 -left-1/3 w-2/3 rotate-12 bg-white/[0.05] blur-2xl"
                style={{ animation: "cosSweep 5s ease-in-out infinite" }}
              />

              <div className="absolute left-2.5 top-2.5 z-10 flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-red-400" />
                <span className="text-[9px] font-medium uppercase tracking-widest text-white/60">Playing</span>
              </div>
              <span className="absolute right-2.5 top-2.5 z-10 text-[9px] font-medium text-white/40">{copy.clip}</span>

              <div
                key={scene === "highlights" ? `highlights-${highlightIndex}` : scene}
                className="relative z-10 flex h-full w-full flex-col items-center justify-center gap-2 px-4"
                style={{ animation: "cosFade 0.5s ease-out" }}
              >
                {scene === "logo" && (
                  <>
                    <img src="/logo-icon.png" alt="" className="h-11 w-11 rounded-xl object-cover" />
                    <span className="text-center text-[11px] font-semibold tracking-[0.12em] text-white/90">
                      SYNAPSE-X-CREATOROS
                    </span>
                  </>
                )}

                {scene === "title" && (
                  <>
                    <p className="text-center text-[16px] font-semibold leading-snug text-white">{copy.clip}</p>
                    <span className="text-[9px] font-medium uppercase tracking-widest text-white/40">
                      An AI-generated video
                    </span>
                  </>
                )}

                {scene === "highlights" &&
                  (() => {
                    const item = CLIP_HIGHLIGHTS[highlightIndex];
                    const Icon = item.icon;
                    return (
                      <div className="flex items-center gap-2">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-violet-400/15">
                          <Icon className="h-3.5 w-3.5 text-violet-300" />
                        </div>
                        <span className="text-[13px] font-medium text-white/90">{item.label}</span>
                        <Sparkles className="h-3 w-3 text-violet-300/70" />
                      </div>
                    );
                  })()}
              </div>

              <div className="absolute bottom-4 left-0 z-10 flex h-4 w-full items-end justify-center gap-[3px] px-6">
                {Array.from({ length: 28 }).map((_, i) => (
                  <span
                    key={i}
                    className="w-[2px] rounded-full bg-violet-300/70"
                    style={{
                      height: "100%",
                      transformOrigin: "bottom",
                      animation: "cosWave 1.1s ease-in-out infinite",
                      animationDelay: `${i * 0.05}s`,
                    }}
                  />
                ))}
              </div>

              <div className="absolute bottom-0 left-0 z-10 h-1 w-full bg-white/10">
                <div className="h-full bg-violet-400" style={{ width: `${videoProgress}%` }} />
              </div>

              <style>{`
                @keyframes cosWave { 0%, 100% { transform: scaleY(0.25); } 50% { transform: scaleY(1); } }
                @keyframes cosSweep { 0% { transform: translateX(-20%) rotate(12deg); } 50% { transform: translateX(20%) rotate(12deg); } 100% { transform: translateX(-20%) rotate(12deg); } }
                @keyframes cosFade { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }
              `}</style>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
