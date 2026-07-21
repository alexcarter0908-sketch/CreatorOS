# CreatorOS - Auth pages redesign (login/signup)
# Run this from your project ROOT (the folder that contains "frontend").
# It will CREATE/OVERWRITE the files below. Backups are made first (.bak).

$ErrorActionPreference = "Stop"

function Write-FileSafely($path, $content) {
    $dir = Split-Path $path -Parent
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    if (Test-Path $path) {
        Copy-Item $path "$path.bak" -Force
    }
    Set-Content -Path $path -Value $content -NoNewline
    Write-Host "Wrote: $path"
}

$authShowcasePanel = @'
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
'@
Write-FileSafely "frontend/features/auth/components/AuthShowcasePanel.tsx" $authShowcasePanel

$authShell = @'
import type { ReactNode } from "react";
import AuthShowcasePanel from "./AuthShowcasePanel";

export default function AuthShell({
  children,
  variant,
}: {
  children: ReactNode;
  variant: "login" | "register";
}) {
  return (
    <div className="flex min-h-screen w-full bg-background">
      <div className="flex w-full flex-col items-center justify-center px-6 py-12 lg:w-[46%] lg:px-16 xl:px-20">
        {children}
      </div>
      <AuthShowcasePanel variant={variant} />
    </div>
  );
}
'@
Write-FileSafely "frontend/features/auth/components/AuthShell.tsx" $authShell

$loginPage = @'
import AuthShell from "@/features/auth/components/AuthShell";
import LoginForm from "@/features/auth/components/LoginForm";

export default function LoginPage() {
  return (
    <AuthShell variant="login">
      <LoginForm />
    </AuthShell>
  );
}
'@
Write-FileSafely "frontend/app/login/page.tsx" $loginPage

$registerPage = @'
import AuthShell from "@/features/auth/components/AuthShell";
import RegisterForm from "@/features/auth/components/RegisterForm";

export default function RegisterPage() {
  return (
    <AuthShell variant="register">
      <RegisterForm />
    </AuthShell>
  );
}
'@
Write-FileSafely "frontend/app/register/page.tsx" $registerPage

$loginForm = @'
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "../store/auth.store";

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden="true">
      <path fill="#4285F4" d="M23.49 12.27c0-.82-.07-1.42-.22-2.05H12v3.72h6.5c-.13 1.05-.84 2.63-2.42 3.7l3.72 2.88c2.22-2.05 3.7-5.06 3.7-8.25z" />
      <path fill="#34A853" d="M12 24c3.24 0 5.95-1.07 7.94-2.9l-3.72-2.88c-1.03.69-2.36 1.16-4.22 1.16-3.24 0-5.98-2.18-6.96-5.11H1.2v3.2C3.18 21.3 7.26 24 12 24z" />
      <path fill="#FBBC05" d="M5.04 14.27c-.25-.75-.4-1.55-.4-2.27s.15-1.52.4-2.27V6.53H1.2C.44 8.05 0 9.97 0 12s.44 3.95 1.2 5.47l3.84-3.2z" />
      <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.26 0 3.18 2.7 1.2 6.53l3.84 3.2c.98-2.93 3.72-5.11 6.96-5.11z" />
    </svg>
  );
}

export default function LoginForm() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      await login({ email, password });
      router.push("/command-center");
    } catch (error: any) {
      const status: number | undefined = error?.response?.status;
      const detail: string | undefined = error?.response?.data?.detail;

      if (detail && detail.toLowerCase().includes("verify")) {
        toast.error("Please verify your email first.");
        router.push(`/verify-email?email=${encodeURIComponent(email)}`);
        return;
      }

      // BUG FIX: previously any error without a `detail` field (timeouts,
      // network failures, 5xx server errors) fell through to "Invalid
      // email or password" - which is actively misleading when the
      // password is actually correct and the real problem is that the
      // request never completed. Each case below now says what actually
      // happened.
      if (error?.code === "ECONNABORTED") {
        toast.error("The server took too long to respond. Please try again in a moment.");
        return;
      }

      if (!error?.response) {
        toast.error("Couldn't reach the server. Check your connection and try again.");
        return;
      }

      if (status && status >= 500) {
        toast.error("Something went wrong on our end. Please try again in a moment.");
        return;
      }

      // Only a genuine 401/400 with no more specific detail falls back to this.
      toast.error(detail || "Invalid email or password.");
    }
  }

  function handleGoogleLogin() {
    const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    window.location.href = `${apiBase}/api/v1/auth/google/login`;
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-5">
      <div className="mb-2 flex items-center gap-2 lg:hidden">
        <img src="/logo.png" alt="CreatorOS" className="h-8 w-8 rounded-lg object-cover" />
        <span className="text-sm font-semibold text-foreground">CreatorOS</span>
      </div>

      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold text-foreground">Welcome back</h1>
        <p className="text-sm text-muted-foreground">Sign in to keep creating.</p>
      </div>

      <Button
        type="button"
        variant="outline"
        onClick={handleGoogleLogin}
        className="flex h-10 w-full items-center justify-center gap-2"
      >
        <GoogleIcon />
        Sign in with Google
      </Button>

      <div className="flex items-center gap-3">
        <div className="h-px flex-1 bg-border" />
        <span className="text-xs text-muted-foreground">OR</span>
        <div className="h-px flex-1 bg-border" />
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="h-10"
          required
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="password">Password</Label>
          <a href="/forgot-password" className="text-sm font-medium text-primary hover:underline">
            Forgot password?
          </a>
        </div>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="h-10 pr-10"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            className="absolute right-0 top-0 flex h-10 w-10 items-center justify-center text-muted-foreground hover:text-foreground"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <Button type="submit" className="h-10 w-full" disabled={isLoading}>
        {isLoading ? "Signing in..." : "Login"}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <a href="/register" className="font-medium text-primary hover:underline">
          Register
        </a>
      </p>
    </form>
  );
}
'@
Write-FileSafely "frontend/features/auth/components/LoginForm.tsx" $loginForm

$registerForm = @'
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Eye, EyeOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useAuthStore } from "../store/auth.store";

export default function RegisterForm() {
  const router = useRouter();

  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    try {
      const verifiedEmail = await register({ full_name: fullName, email, password });
      toast.success("Account created! Check your email for a verification code.");
      router.push(`/verify-email?email=${encodeURIComponent(verifiedEmail)}`);
    } catch {
      toast.error("Registration failed. Try a different email.");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-5">
      <div className="mb-2 flex items-center gap-2 lg:hidden">
        <img src="/logo.png" alt="CreatorOS" className="h-8 w-8 rounded-lg object-cover" />
        <span className="text-sm font-semibold text-foreground">CreatorOS</span>
      </div>

      <div className="space-y-1.5">
        <h1 className="text-2xl font-semibold text-foreground">Create account</h1>
        <p className="text-sm text-muted-foreground">Start creating with your own AI command center.</p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="fullName">Full name</Label>
        <Input
          id="fullName"
          placeholder="Jane Doe"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="h-10"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="h-10"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            placeholder="At least 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="h-10 pr-10"
            minLength={8}
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            className="absolute right-0 top-0 flex h-10 w-10 items-center justify-center text-muted-foreground hover:text-foreground"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <Button type="submit" className="h-10 w-full" disabled={isLoading}>
        {isLoading ? "Creating..." : "Register"}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <a href="/login" className="font-medium text-primary hover:underline">
          Login
        </a>
      </p>
    </form>
  );
}
'@
Write-FileSafely "frontend/features/auth/components/RegisterForm.tsx" $registerForm

Write-Host ""
Write-Host "Done. Restart your dev server (npm run dev) and open /login or /register." -ForegroundColor Green
