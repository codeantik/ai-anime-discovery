"use client";

import { motion } from "framer-motion";
import { ExternalLink, Star } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { AddToAniListButton } from "@/components/AddToAniListButton";
import { AddToMALButton } from "@/components/AddToMALButton";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";

interface Props {
  anime: AnimeRecommendation;
  index: number;
}

export function AnimeCard({ anime, index }: Props) {
  const router = useRouter();
  const score = anime.mean_score ? (anime.mean_score / 10).toFixed(1) : null;
  const meta = [anime.year, anime.format, anime.episodes ? `${anime.episodes} ep` : null]
    .filter(Boolean)
    .join(" · ");

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      role="link"
      tabIndex={0}
      onClick={() => router.push(`/anime/${anime.anilist_id}`)}
      onKeyDown={(e) => e.key === "Enter" && router.push(`/anime/${anime.anilist_id}`)}
      className="group flex cursor-pointer flex-col overflow-hidden rounded-2xl border border-white/8 bg-white/4 backdrop-blur-md transition-all duration-300 hover:border-purple-500/30 hover:bg-white/8 hover:shadow-[0_0_30px_rgba(168,85,247,0.12)]"
    >
      {/* Cover image */}
      <div className="relative aspect-[3/4] w-full overflow-hidden bg-slate-900">
        {anime.cover_image ? (
          <Image
            src={anime.cover_image}
            alt={anime.title}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-gradient-to-br from-purple-900/40 to-indigo-900/40 text-4xl text-white/20">
            🎌
          </div>
        )}
        {score && (
          <div className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-1 text-xs font-bold text-yellow-400 backdrop-blur-sm">
            <Star className="h-3 w-3 fill-yellow-400" />
            {score}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex flex-1 flex-col gap-2 p-4">
        <div>
          <h3 className="line-clamp-2 font-bold leading-snug text-white">{anime.title}</h3>
          {meta && <p className="mt-0.5 text-xs text-slate-500">{meta}</p>}
        </div>

        {anime.genres.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {anime.genres.slice(0, 3).map((g) => (
              <span key={g} className="rounded-full bg-indigo-500/15 px-2 py-0.5 text-xs text-indigo-300">
                {g}
              </span>
            ))}
          </div>
        )}

        {anime.recommended_because && (
          <p className="mt-auto text-xs leading-relaxed text-slate-400 line-clamp-3">
            <span className="font-medium text-purple-400">Why you&apos;ll love it: </span>
            {anime.recommended_because}
          </p>
        )}

        <div className="mt-2 flex items-center justify-between">
          <a
            href={`https://anilist.co/anime/${anime.anilist_id}`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-xs text-slate-600 transition-colors hover:text-purple-400"
          >
            AniList <ExternalLink className="h-3 w-3" />
          </a>
          <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
            <AddToAniListButton anilistId={anime.anilist_id} />
            <AddToMALButton anilistId={anime.anilist_id} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
