"use client";

import { motion } from "framer-motion";
import { Loader2, Sparkles } from "lucide-react";
import { useEffect } from "react";
import { AnimeCard } from "@/components/AnimeCard";
import { ShareDigestButton } from "@/components/ShareDigestButton";
import { BACKEND_URL } from "@/lib/backendUrl";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useDigest, useMarkDigestViewed } from "@/lib/hooks/useDigest";

export default function DigestPage() {
  const { data: user, isLoading: userLoading } = useAniListUser();
  const { data: digest, isLoading: digestLoading } = useDigest();
  const { mutate: markViewed } = useMarkDigestViewed();

  useEffect(() => {
    if (digest?.available && !digest.viewed) {
      markViewed();
    }
  }, [digest?.available, digest?.viewed, markViewed]);

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
        <Sparkles className="h-10 w-10 text-purple-400/60" />
        <p className="max-w-sm text-slate-400">
          Connect your AniList account to get a personalized digest of new picks.
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

  if (digestLoading) {
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
        className="mb-8 flex flex-wrap items-start justify-between gap-3"
      >
        <div>
          <h1 className="text-2xl font-bold text-white">
            New{" "}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              For You
            </span>
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {digest?.generated_at
              ? `Refreshed ${new Date(digest.generated_at).toLocaleString()}`
              : "Picks based on your taste vector, refreshed daily."}
          </p>
        </div>
        {digest?.available && <ShareDigestButton />}
      </motion.div>

      {!digest?.available ? (
        <div className="flex flex-col items-center gap-2 py-16 text-center text-slate-500">
          <Sparkles className="h-8 w-8 text-slate-700" />
          Not enough taste signal yet — rate a few anime or sync your AniList history to unlock
          your digest.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {digest.recommendations.map((anime, i) => (
            <AnimeCard key={anime.anilist_id} anime={anime} index={i} />
          ))}
        </div>
      )}
    </main>
  );
}
