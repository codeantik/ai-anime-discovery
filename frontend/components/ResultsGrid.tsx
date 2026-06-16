"use client";

import { motion } from "framer-motion";
import { Download, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AnimeCard } from "@/components/AnimeCard";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";

interface Props {
  recommendations: AnimeRecommendation[];
  queryUsed: string;
  onReset: () => void;
}

function exportJSON(data: AnimeRecommendation[]) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "anime-picks.json";
  a.click();
  URL.revokeObjectURL(url);
}

function exportCSV(data: AnimeRecommendation[]) {
  const headers = ["Title", "Year", "Score", "Format", "Episodes", "Genres", "Why You'll Love It", "AniList URL"];
  const rows = data.map((r) => [
    r.title,
    r.year ?? "",
    r.mean_score ?? "",
    r.format ?? "",
    r.episodes ?? "",
    r.genres.join("; "),
    r.recommended_because,
    `https://anilist.co/anime/${r.anilist_id}`,
  ]);
  const csv = [headers, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
    .join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "anime-picks.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export function ResultsGrid({ recommendations, queryUsed, onReset }: Props) {
  return (
    <div className="w-full">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-white">
            Your picks{" "}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              ({recommendations.length})
            </span>
          </h2>
          <p className="mt-1 line-clamp-1 max-w-md text-xs text-slate-500">
            Based on: <span className="text-slate-400">{queryUsed}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Export buttons */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => exportCSV(recommendations)}
            className="rounded-full border border-white/10 text-slate-400 hover:text-white"
          >
            <Download className="mr-1.5 h-3.5 w-3.5" /> CSV
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => exportJSON(recommendations)}
            className="rounded-full border border-white/10 text-slate-400 hover:text-white"
          >
            <Download className="mr-1.5 h-3.5 w-3.5" /> JSON
          </Button>
          <Button
            size="sm"
            onClick={onReset}
            className="rounded-full bg-white/8 px-4 text-slate-300 hover:bg-white/12 hover:text-white"
          >
            <RefreshCw className="mr-1.5 h-3.5 w-3.5" /> Start over
          </Button>
        </div>
      </motion.div>

      {/* Grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {recommendations.map((anime, i) => (
          <AnimeCard key={anime.anilist_id} anime={anime} index={i} />
        ))}
      </div>
    </div>
  );
}
