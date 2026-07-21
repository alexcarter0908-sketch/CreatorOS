"use client";

interface BrandWatermarkProps {
  /** Controls fade in/out - used by Command Center to hide it once the
   * user starts typing or a conversation exists. Dashboard always passes
   * true (or omits this) since it should stay put. */
  visible?: boolean;
  /** "compact" (default) = small, grayscale, used on the Dashboard.
   * "hero" = big, original brand colors, near-fullscreen - used on the
   * Command Center's welcome screen. Kept low-opacity either way so
   * foreground text always stays fully readable on top of it. */
  variant?: "compact" | "hero";
}

export default function BrandWatermark({ visible = true, variant = "compact" }: BrandWatermarkProps) {
  const isHero = variant === "hero";

  return (
    <div
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 -z-10 flex items-center justify-center transition-opacity duration-700 ease-out ${
        visible ? (isHero ? "opacity-[0.09]" : "opacity-[0.05]") : "opacity-0"
      }`}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/logo.png"
        alt=""
        className={
          isHero
            ? "h-[85vh] w-[85vh] max-w-none select-none object-contain"
            : "h-[46vh] w-[46vh] max-w-none select-none object-contain grayscale"
        }
        draggable={false}
      />
    </div>
  );
}
