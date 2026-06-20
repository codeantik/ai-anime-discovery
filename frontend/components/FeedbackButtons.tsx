"use client";

import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useFeedback, useSetFeedback } from "@/lib/hooks/useFeedback";

interface Props {
  anilistId: number;
}

export function FeedbackButtons({ anilistId }: Props) {
  const { data: user } = useAniListUser();
  const { data: feedback } = useFeedback();
  const { mutate: setFeedback, isPending } = useSetFeedback();

  if (!user) return null;

  const signal = feedback?.[String(anilistId)] ?? 0;

  const toggle = (next: 1 | -1) => {
    if (isPending) return;
    setFeedback({ anilist_id: anilistId, signal: signal === next ? 0 : next });
  };

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => toggle(1)}
        disabled={isPending}
        title={signal === 1 ? "Remove like" : "I like this"}
        className={`rounded-full p-1.5 transition-all duration-200
          ${signal === 1
            ? "border border-emerald-500/30 bg-emerald-500/15 text-emerald-400"
            : "border border-white/10 bg-white/5 text-slate-400 hover:border-emerald-400/40 hover:text-emerald-300"
          } disabled:cursor-not-allowed`}
      >
        <ThumbsUp className="h-3 w-3" fill={signal === 1 ? "currentColor" : "none"} />
      </button>
      <button
        onClick={() => toggle(-1)}
        disabled={isPending}
        title={signal === -1 ? "Remove dislike" : "Not for me"}
        className={`rounded-full p-1.5 transition-all duration-200
          ${signal === -1
            ? "border border-rose-500/30 bg-rose-500/15 text-rose-400"
            : "border border-white/10 bg-white/5 text-slate-400 hover:border-rose-400/40 hover:text-rose-300"
          } disabled:cursor-not-allowed`}
      >
        <ThumbsDown className="h-3 w-3" fill={signal === -1 ? "currentColor" : "none"} />
      </button>
    </div>
  );
}
