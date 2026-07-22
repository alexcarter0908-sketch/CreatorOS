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
        <img src="/logo.png" alt="Synapse-X-CreatorOS" className="h-8 w-8 shrink-0 rounded-lg object-cover" />
        <span className="text-sm font-semibold text-foreground">Synapse-X-CreatorOS</span>
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