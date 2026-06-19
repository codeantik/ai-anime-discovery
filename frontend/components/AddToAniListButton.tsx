"use client";

import { Check, Loader2, Plus } from "lucide-react";
import { useState } from "react";
import { useAddToList, useAniListUser } from "@/lib/hooks/useAniListAuth";

interface Props {
  anilistId: number;
}

export function AddToAniListButton({ anilistId }: Props) {
  const { data: user } = useAniListUser();
  const { mutate, isPending } = useAddToList();
  const [added, setAdded] = useState(false);

  if (!user) return null;

  return (
    <button
      onClick={() => !added && !isPending && mutate({ anilist_id: anilistId }, { onSuccess: () => setAdded(true) })}
      disabled={isPending || added}
      title={added ? "Added to AniList" : "Add to Plan to Watch"}
      className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-200
        ${added
          ? "border border-green-500/30 bg-green-500/15 text-green-400"
          : "border border-teal-500/20 bg-teal-500/10 text-teal-300 hover:border-teal-400/40 hover:bg-teal-500/20"
        } disabled:cursor-not-allowed`}
    >
      {isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : added ? <Check className="h-3 w-3" /> : <Plus className="h-3 w-3" />}
      {added ? "Added" : "AniList"}
    </button>
  );
}
