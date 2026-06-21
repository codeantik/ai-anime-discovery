"use client";

import { Check, Loader2, Share2 } from "lucide-react";
import { useState } from "react";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useCreateCardShare } from "@/lib/hooks/useShare";

interface Props {
  anilistId: number;
  recommendedBecause?: string;
}

export function ShareButton({ anilistId, recommendedBecause }: Props) {
  const { data: user } = useAniListUser();
  const { mutate, isPending } = useCreateCardShare();
  const [copied, setCopied] = useState(false);

  if (!user) return null;

  const handleClick = () => {
    if (isPending) return;
    mutate(
      { anilist_id: anilistId, recommended_because: recommendedBecause },
      {
        onSuccess: async ({ token }) => {
          await navigator.clipboard.writeText(`${window.location.origin}/share/${token}`);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        },
      }
    );
  };

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
      title="Copy a shareable link"
      className={`flex cursor-pointer items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-200
        ${copied
          ? "border border-emerald-500/30 bg-emerald-500/15 text-emerald-400"
          : "border border-sky-500/20 bg-sky-500/10 text-sky-300 hover:border-sky-400/40 hover:bg-sky-500/20"
        } disabled:cursor-not-allowed`}
    >
      {isPending ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : copied ? (
        <Check className="h-3 w-3" />
      ) : (
        <Share2 className="h-3 w-3" />
      )}
      {copied ? "Copied!" : "Share"}
    </button>
  );
}
