"use client";

import { motion } from "framer-motion";
import { Bookmark, Loader2 } from "lucide-react";
import { useState } from "react";
import { AnimeCard } from "@/components/AnimeCard";
import { ShareWatchlistButton } from "@/components/ShareWatchlistButton";
import { BACKEND_URL } from "@/lib/backendUrl";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useWatchlist, WatchlistSort } from "@/lib/hooks/useWatchlist";

export default function WatchlistPage() {
  const [sort, setSort] = useState<WatchlistSort>("added");
  const { data: user, isLoading: userLoading } = useAniListUser();
  const { data: watchlist, isLoading: watchlistLoading } = useWatchlist(sort);

  if (userLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-[70vh] flex-col items-center justify-center gap-4 px-4 text-center">
        <Bookmark className="h-10 w-10 text-amber-400/60" />
        <p className="max-w-sm text-slate-400">
          Connect your AniList account to save anime to your watchlist.
        </p>
        <motion.a
          href={`${BACKEND_URL}/auth/anilist/login`}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className="inline-flex items-center gap-2 rounded-full border border-teal-500/30 bg-teal-500/10 px-4 py-1.5 text-sm font-medium text-teal-300 transition-colors hover:border-teal-400/50 hover:bg-teal-500/20"
        >
          Connect AniList
        </motion.a>
      </main>
    );
  }

  if (watchlistLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 pb-20 pt-8">
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8 flex flex-wrap items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-white">
            Your{" "}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Watchlist
            </span>
          </h1>
          <p className="mt-1 text-sm text-slate-500">Anime you&apos;ve saved for later.</p>
        </div>
        {watchlist && watchlist.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 rounded-full border border-white/10 bg-white/5 p-1 text-sm">
              <button
                onClick={() => setSort("added")}
                className={`rounded-full px-3 py-1 transition-colors ${
                  sort === "added"
                    ? "bg-purple-500/30 text-purple-200"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Date added
              </button>
              <button
                onClick={() => setSort("taste")}
                className={`rounded-full px-3 py-1 transition-colors ${
                  sort === "taste"
                    ? "bg-purple-500/30 text-purple-200"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Taste match
              </button>
            </div>
            <ShareWatchlistButton />
          </div>
        )}
      </motion.div>

      {!watchlist || watchlist.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-16 text-center text-slate-500">
          <Bookmark className="h-8 w-8 text-slate-700" />
          Your watchlist is empty — bookmark anime to save them here.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {watchlist.map((anime, i) => (
            <AnimeCard key={anime.anilist_id} anime={anime} index={i} />
          ))}
        </div>
      )}
    </main>
  );
}
