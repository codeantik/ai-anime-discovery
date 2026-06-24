"use client";

import { motion } from "framer-motion";
import { Loader2, Users } from "lucide-react";
import { useParams } from "next/navigation";
import { AnimeCard } from "@/components/AnimeCard";
import { ConnectToDiscoverBanner } from "@/components/ConnectToDiscoverBanner";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useDuoRecommendations } from "@/lib/hooks/useDuo";

export default function DuoPage() {
  const { token } = useParams<{ token: string }>();
  const { data: user } = useAniListUser();
  const { data, isLoading, isError, error } = useDuoRecommendations(token);

  if (isLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </main>
    );
  }

  if (isError || !data) {
    return (
      <main className="flex min-h-[70vh] flex-col items-center justify-center gap-2 px-4 text-center">
        <Users className="h-10 w-10 text-slate-700" />
        <p className="max-w-sm text-slate-400">
          {error instanceof Error ? error.message : "This invite link is invalid or has expired."}
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 pb-20 pt-8">
      {!user && <ConnectToDiscoverBanner />}

      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-2xl font-bold text-white">
          {data.combined ? (
            <>
              Picks for{" "}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                both of you
              </span>
            </>
          ) : (
            <>
              A friend&apos;s{" "}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                taste
              </span>
            </>
          )}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {data.combined
            ? "Recommendations blended from both your taste vectors."
            : user
              ? "Connect more AniList history or rate a few anime to blend your own taste in."
              : "Connect AniList to blend your own taste in and see recommendations for both of you."}
        </p>
      </motion.div>

      {data.recommendations.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-16 text-center text-slate-500">
          <Users className="h-8 w-8 text-slate-700" />
          No matches yet — check back later.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {data.recommendations.map((anime, i) => (
            <AnimeCard key={anime.anilist_id} anime={anime} index={i} />
          ))}
        </div>
      )}
    </main>
  );
}
