"use client";

import { Check, Loader2, Plus } from "lucide-react";
import { useState } from "react";
import { useAddToMAL, useMALUser } from "@/lib/hooks/useMALAuth";

interface Props {
  anilistId: number;
}

export function AddToMALButton({ anilistId }: Props) {
  const { data: user } = useMALUser();
  const { mutate, isPending } = useAddToMAL();
  const [added, setAdded] = useState(false);

  if (!user) return null;

  return (
    <button
      onClick={() => !added && !isPending && mutate({ anilist_id: anilistId }, { onSuccess: () => setAdded(true) })}
      disabled={isPending || added}
      title={added ? "Added to MyAnimeList" : "Add to Plan to Watch"}
      className={`flex cursor-pointer items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-200
        ${added
          ? "border border-green-500/30 bg-green-500/15 text-green-400"
          : "border border-blue-500/20 bg-blue-500/10 text-blue-300 hover:border-blue-400/40 hover:bg-blue-500/20"
        } disabled:cursor-not-allowed`}
    >
      {isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : added ? <Check className="h-3 w-3" /> : <Plus className="h-3 w-3" />}
      {added ? "Added" : "MAL"}
    </button>
  );
}
