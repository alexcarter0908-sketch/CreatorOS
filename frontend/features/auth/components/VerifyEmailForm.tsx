"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient, ACCESS_TOKEN_KEY } from "@/lib/api/client";

export default function VerifyEmailForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState(searchParams.get("email") || "");
  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);
    try {
      const { data } = await apiClient.post("/api/v1/auth/verify-email", {
        email,
        otp_code: otp,
      });
      localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
      toast.success("Email verified!");
      router.push("/");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Verification failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleResend() {
    setIsResending(true);
    try {
      await apiClient.post("/api/v1/auth/resend-verification", { email });
      toast.success("Naya code bhej diya gaya hai.");
    } catch {
      toast.error("Resend failed.");
    } finally {
      setIsResending(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-md space-y-4 rounded-2xl border border-border bg-card p-8 shadow-sm"
    >
      <div>
        <h1 className="text-3xl font-bold text-foreground">Verify your email</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Humne aapke email par ek 6-digit code bheja hai. Usay neeche daal dein.
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="otp">Verification code</Label>
        <Input
          id="otp"
          type="text"
          inputMode="numeric"
          maxLength={6}
          placeholder="000000"
          value={otp}
          onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
          className="text-center text-2xl tracking-[0.5em]"
          required
        />
      </div>

      <Button type="submit" className="w-full" disabled={isLoading || otp.length !== 6}>
        {isLoading ? "Verifying..." : "Verify"}
      </Button>

      <p className="text-center text-xs text-muted-foreground">
        Can't find the message? Check your Spam/Junk folder too.
      </p>

      <button
        type="button"
        onClick={handleResend}
        disabled={isResending}
        className="w-full text-center text-sm font-medium text-primary hover:underline"
      >
        {isResending ? "Sending..." : "Resend code"}
      </button>
    </form>
  );
}
