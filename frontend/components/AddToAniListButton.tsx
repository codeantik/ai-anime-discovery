"use client";

import { Check, Loader2, Plus } from "lucide-react";
import { useAddToList, useAniListIds, useAniListUser } from "@/lib/hooks/useAniListAuth";

interface Props {
  anilistId: number;
}

export function AddToAniListButton({ anilistId }: Props) {
  const { data: user } = useAniListUser();
  const { data: ids } = useAniListIds();
  const { mutate, isPending } = useAddToList();

  if (!user) return null;

  const isAdded = ids?.includes(anilistId) ?? false;

  return (
    <button
      onClick={() => !isAdded && !isPending && mutate({ anilist_id: anilistId })}
      disabled={isPending || isAdded}
      title={isAdded ? "Already on AniList" : "Add to Plan to Watch"}
      className={`flex cursor-pointer items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-200
        ${isAdded
          ? "border border-green-500/30 bg-green-500/15 text-green-400"
          : "border border-teal-500/20 bg-teal-500/10 text-teal-300 hover:border-teal-400/40 hover:bg-teal-500/20"
        } disabled:cursor-not-allowed`}
    >
      {isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : isAdded ? <Check className="h-3 w-3" /> : <Plus className="h-3 w-3" />}
      {isAdded ? "Added" : "AniList"}
    </button>
  );
}
