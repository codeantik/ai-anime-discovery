"use client";

import { Check, Loader2, Share2 } from "lucide-react";
import { useState } from "react";
import { useCreateWatchlistShare } from "@/lib/hooks/useShare";

export function ShareWatchlistButton() {
  const { mutate, isPending } = useCreateWatchlistShare();
  const [copied, setCopied] = useState(false);

  const handleClick = () => {
    if (isPending) return;
    mutate(undefined, {
      onSuccess: async ({ token }) => {
        await navigator.clipboard.writeText(`${window.location.origin}/share/${token}`);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      },
    });
  };

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
      className={`flex shrink-0 cursor-pointer items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition-all duration-200
        ${copied
          ? "border border-emerald-500/30 bg-emerald-500/15 text-emerald-400"
          : "border border-sky-500/20 bg-sky-500/10 text-sky-300 hover:border-sky-400/40 hover:bg-sky-500/20"
        } disabled:cursor-not-allowed`}
    >
      {isPending ? (
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
      ) : copied ? (
        <Check className="h-3.5 w-3.5" />
      ) : (
        <Share2 className="h-3.5 w-3.5" />
      )}
      {copied ? "Link copied!" : "Share watchlist"}
    </button>
  );
}
