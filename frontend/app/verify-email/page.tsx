import { Suspense } from "react";
import VerifyEmailForm from "@/features/auth/components/VerifyEmailForm";

export default function VerifyEmailPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background">
      <Suspense fallback={null}>
        <VerifyEmailForm />
      </Suspense>
    </main>
  );
}
