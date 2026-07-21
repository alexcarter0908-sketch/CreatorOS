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