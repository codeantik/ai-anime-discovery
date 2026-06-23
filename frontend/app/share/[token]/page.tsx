"use client";

import { motion } from "framer-motion";
import { Loader2, Share2 } from "lucide-react";
import { useParams } from "next/navigation";
import { AnimeCard } from "@/components/AnimeCard";
import { ConnectToDiscoverBanner } from "@/components/ConnectToDiscoverBanner";
import { useSharedContent } from "@/lib/hooks/useShare";

export default function SharePage() {
  const { token } = useParams<{ token: string }>();
  const { data, isLoading, isError, error } = useSharedContent(token);

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
        <Share2 className="h-10 w-10 text-slate-700" />
        <p className="max-w-sm text-slate-400">
          {error instanceof Error ? error.message : "This share link is invalid or has expired."}
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 pb-20 pt-8">
      <ConnectToDiscoverBanner />

      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-2xl font-bold text-white">
          {data.type === "card" ? (
            <>
              An anime{" "}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                pick
              </span>{" "}
              shared with you
            </>
          ) : data.type === "digest" ? (
            <>
              A shared{" "}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                digest
              </span>
            </>
          ) : (
            <>
              A shared{" "}
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                watchlist
              </span>
            </>
          )}
        </h1>
        {data.type === "digest" && data.generated_at && (
          <p className="mt-1 text-sm text-slate-500">
            Refreshed {new Date(data.generated_at).toLocaleString()}
          </p>
        )}
      </motion.div>

      {data.anime.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-16 text-center text-slate-500">
          <Share2 className="h-8 w-8 text-slate-700" />
          {data.type === "digest" ? "This digest is empty." : "This watchlist is empty."}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {data.anime.map((anime, i) => (
            <AnimeCard key={anime.anilist_id} anime={anime} index={i} />
          ))}
        </div>
      )}
    </main>
  );
}
