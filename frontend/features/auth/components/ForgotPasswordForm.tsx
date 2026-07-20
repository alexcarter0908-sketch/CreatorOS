"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CheckCircle2 } from "lucide-react";

export default function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);

    // TODO: backend ready hone par yahan actual API call lagegi, e.g.:
    // await authService.forgotPassword(email);
    await new Promise((resolve) => setTimeout(resolve, 800));

    setIsLoading(false);
    setSubmitted(true);
    toast.success("Agar ye email registered hai, reset link bhej diya gaya hai.");
  }

  if (submitted) {
    return (
      <div className="w-full max-w-md space-y-4 rounded-2xl border border-border bg-card p-8 text-center shadow-sm">
        <CheckCircle2 className="mx-auto h-12 w-12 text-primary" />
        <h1 className="text-2xl font-bold text-foreground">Check your email</h1>
        <p className="text-sm text-muted-foreground">
          Agar <span className="font-medium text-foreground">{email}</span> se koi account juda hai,
          hum ne us par password reset karne ka link bhej diya hai.
        </p>
        <a href="/login" className="inline-block text-sm font-medium text-primary hover:underline">
          Back to login
        </a>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-md space-y-4 rounded-2xl border border-border bg-card p-8 shadow-sm"
    >
      <div>
        <h1 className="text-3xl font-bold text-foreground">Forgot password?</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Apna email daalein, hum aapko reset link bhej denge.
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Sending..." : "Send reset link"}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        Remembered your password?{" "}
        <a href="/login" className="font-medium text-primary hover:underline">
          Back to login
        </a>
      </p>
    </form>
  );
}
