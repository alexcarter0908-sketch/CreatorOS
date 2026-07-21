"use client";

import Link from "next/link";

interface AssetLibraryProps {
  scripts: number;
  images: number;
  videos: number;
  audio: number;
  isLoading?: boolean;
}

export default function AssetLibrary({
  scripts,
  images,
  videos,
  audio,
  isLoading = false,
}: AssetLibraryProps) {
  const tiles = [
    { label: "Scripts", count: scripts },
    { label: "Images", count: images },
    { label: "Videos", count: videos },
    { label: "Audio", count: audio },
  ];

  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold tracking-tight text-foreground">Asset Library</h2>
        <Link href="/assets" className="text-sm font-medium text-primary hover:underline">
          Manage
        </Link>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {tiles.map((tile) => (
          <div
            key={tile.label}
            className="rounded-xl border border-border/60 bg-accent/40 px-4 py-3.5"
          >
            <div className="font-console-display text-2xl font-semibold text-foreground">
              {isLoading ? "-" : tile.count.toLocaleString()}
            </div>
            <div className="mt-0.5 text-xs text-muted-foreground">{tile.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
