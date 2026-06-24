"use client";

import { motion } from "framer-motion";
import { Loader2, Radar } from "lucide-react";
import { AnimeCard } from "@/components/AnimeCard";
import { useSeasonal } from "@/lib/hooks/useSeasonal";

const SEASON_LABELS: Record<string, string> = {
  WINTER: "Winter",
  SPRING: "Spring",
  SUMMER: "Summer",
  FALL: "Fall",
};

export default function SeasonalPage() {
  const { data, isLoading } = useSeasonal();

  if (isLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </main>
    );
  }

  const seasonLabel = data ? SEASON_LABELS[data.season] ?? data.season : "";

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 pb-20 pt-8">
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-2xl font-bold text-white">
          {seasonLabel} {data?.year}{" "}
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Radar
          </span>
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {data?.personalized
            ? "New and airing anime this season, ranked by your taste."
            : "New and airing anime this season, ranked by popularity — connect AniList to personalize this."}
        </p>
      </motion.div>

      {!data || data.anime.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-16 text-center text-slate-500">
          <Radar className="h-8 w-8 text-slate-700" />
          Nothing airing this season matched the catalog yet — check back later.
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
