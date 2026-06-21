"use client";

import { Bookmark, BookmarkCheck, Loader2 } from "lucide-react";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useAddToWatchlist, useRemoveFromWatchlist, useWatchlist } from "@/lib/hooks/useWatchlist";

interface Props {
  anilistId: number;
}

export function AddToWatchlistButton({ anilistId }: Props) {
  const { data: user } = useAniListUser();
  const { data: watchlist } = useWatchlist();
  const { mutate: add, isPending: isAdding } = useAddToWatchlist();
  const { mutate: remove, isPending: isRemoving } = useRemoveFromWatchlist();

  if (!user) return null;

  const isBookmarked = watchlist?.some((a) => a.anilist_id === anilistId) ?? false;
  const isPending = isAdding || isRemoving;

  return (
    <button
      onClick={() => !isPending && (isBookmarked ? remove(anilistId) : add(anilistId))}
      disabled={isPending}
      title={isBookmarked ? "Remove from watchlist" : "Save for later"}
      className={`flex cursor-pointer items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-200
        ${isBookmarked
          ? "border border-amber-500/30 bg-amber-500/15 text-amber-400"
          : "border border-amber-500/20 bg-amber-500/10 text-amber-300 hover:border-amber-400/40 hover:bg-amber-500/20"
        } disabled:cursor-not-allowed`}
    >
      {isPending ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : isBookmarked ? (
        <BookmarkCheck className="h-3 w-3" />
      ) : (
        <Bookmark className="h-3 w-3" />
      )}
      {isBookmarked ? "Saved" : "Save"}
    </button>
  );
}
