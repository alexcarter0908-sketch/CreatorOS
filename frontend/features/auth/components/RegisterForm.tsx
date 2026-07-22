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
        <img src="/logo.png" alt="Synapse-X-CreatorOS" className="h-8 w-8 shrink-0 rounded-lg object-cover" />
        <span className="text-sm font-semibold text-foreground">Synapse-X-CreatorOS</span>
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