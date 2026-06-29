"use client";

import { motion } from "framer-motion";
import { ArrowLeft, ExternalLink, Loader2, Sparkles, Star } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { AddToAniListButton } from "@/components/AddToAniListButton";
import { AddToMALButton } from "@/components/AddToMALButton";
import { AddToWatchlistButton } from "@/components/AddToWatchlistButton";
import { AnimeCard } from "@/components/AnimeCard";
import { useAnimeDetail } from "@/lib/hooks/useAnimeDetail";
import { useSimilarAnime } from "@/lib/hooks/useSimilarAnime";

function humanize(value?: string) {
  if (!value) return null;
  return value
    .toLowerCase()
    .split("_")
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}

function cleanSynopsis(raw: string): string {
  return raw
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .trim();
}

const SYNOPSIS_LIMIT = 400;

function Synopsis({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const cleaned = useMemo(() => cleanSynopsis(text), [text]);
  const isLong = cleaned.length > SYNOPSIS_LIMIT;
  const shown = expanded || !isLong ? cleaned : `${cleaned.slice(0, SYNOPSIS_LIMIT).trimEnd()}…`;

  return (
    <>
      <p className="whitespace-pre-line leading-relaxed text-slate-400">{shown}</p>
      {isLong && (
        <button
          type="button"
          onClick={() => setExpanded((e) => !e)}
          className="mt-2 cursor-pointer text-sm font-medium text-purple-400 transition-colors hover:text-purple-300"
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}
    </>
  );
}

export default function AnimeDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const anilistId = Number(params.id);
  const { data: anime, isLoading, error } = useAnimeDetail(anilistId);
  const { data: similar } = useSimilarAnime(anilistId);

  const goBack = () => {
    if (window.history.length > 1) router.back();
    else router.push("/discover");
  };

  if (isLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </main>
    );
  }

  if (error || !anime) {
    return (
      <main className="flex min-h-[70vh] flex-col items-center justify-center gap-4 text-center">
        <p className="text-slate-400">{error?.message ?? "Anime not found."}</p>
        <Link href="/discover" className="text-purple-400 underline">
          Back to discover
        </Link>
      </main>
    );
  }

  const score = anime.mean_score ? (anime.mean_score / 10).toFixed(1) : null;
  const tasteMatch =
    typeof anime.taste_match === "number" ? Math.round(anime.taste_match * 100) : null;
  const metaItems = [
    anime.year,
    humanize(anime.format ?? undefined),
    anime.episodes ? `${anime.episodes} ep` : null,
    anime.duration ? `${anime.duration} min` : null,
    humanize(anime.status),
  ].filter(Boolean) as string[];

  return (
    <main className="relative min-h-screen pb-20">
      {/* Banner */}
      <div className="pointer-events-none relative h-56 w-full overflow-hidden sm:h-72">
        {anime.banner_image ? (
          <Image src={anime.banner_image} alt="" fill className="object-cover opacity-50" priority />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-purple-900/40 to-indigo-900/40" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-slate-950/10" />
      </div>

      <div className="mx-auto -mt-24 max-w-5xl px-4 sm:-mt-32">
        <button
          type="button"
          onClick={goBack}
          className="mb-4 inline-flex cursor-pointer items-center gap-1.5 rounded-full bg-black/30 px-3 py-1.5 text-sm font-medium text-white/90 backdrop-blur-sm transition-colors hover:bg-black/50 hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" /> Back
        </button>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="flex flex-col gap-6 sm:flex-row"
        >
          {/* Cover */}
          <div className="relative mx-auto aspect-[3/4] w-48 shrink-0 overflow-hidden rounded-2xl border border-white/10 shadow-2xl sm:mx-0">
            {anime.cover_image ? (
              <Image src={anime.cover_image} alt={anime.title} fill sizes="192px" className="object-cover" />
            ) : (
              <div className="flex h-full items-center justify-center bg-gradient-to-br from-purple-900/40 to-indigo-900/40 text-4xl text-white/20">
                🎌
              </div>
            )}
          </div>

          {/* Info */}
          <div className="relative flex flex-1 flex-col gap-3">
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.85)] sm:text-3xl">
                {anime.title}
              </h1>
              {anime.title_romaji && anime.title_romaji !== anime.title && (
                <p className="mt-0.5 text-sm text-slate-500">{anime.title_romaji}</p>
              )}
              {metaItems.length > 0 && (
                <p className="mt-2 break-words text-sm text-slate-400">
                  {metaItems.join(" · ")}
                </p>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {score && (
                <div className="flex items-center gap-1 rounded-full bg-black/40 px-3 py-1 text-sm font-bold text-yellow-400">
                  <Star className="h-4 w-4 fill-yellow-400" />
                  {score}
                </div>
              )}
              {tasteMatch !== null && (
                <div className="flex items-center gap-1 rounded-full bg-purple-500/20 px-3 py-1 text-sm font-bold text-purple-300">
                  <Sparkles className="h-4 w-4" />
                  {tasteMatch}% match for you
                </div>
              )}
              <a
                href={`https://anilist.co/anime/${anime.anilist_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 rounded-full border border-white/10 px-3 py-1 text-sm text-slate-400 transition-colors hover:text-purple-400"
              >
                AniList <ExternalLink className="h-3.5 w-3.5" />
              </a>
              <AddToAniListButton anilistId={anime.anilist_id} />
              <AddToMALButton anilistId={anime.anilist_id} />
              <AddToWatchlistButton anilistId={anime.anilist_id} />
            </div>

            {anime.studios.length > 0 && (
              <p className="text-sm text-slate-500">
                <span className="text-slate-400">Studio:</span> {anime.studios.join(", ")}
              </p>
            )}

            {anime.genres.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {anime.genres.map((g) => (
                  <span key={g} className="rounded-full bg-indigo-500/15 px-2.5 py-1 text-xs text-indigo-300">
                    {g}
                  </span>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {/* Synopsis */}
        {anime.synopsis && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="mt-10"
          >
            <h2 className="mb-2 text-lg font-bold text-white">Synopsis</h2>
            <Synopsis text={anime.synopsis} />
          </motion.section>
        )}

        {/* Tags */}
        {anime.tags.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
            className="mt-8"
          >
            <h2 className="mb-2 text-lg font-bold text-white">Tags</h2>
            <div className="flex flex-wrap gap-1.5">
              {anime.tags.map((t) => (
                <span key={t} className="rounded-full border border-white/8 bg-white/4 px-2.5 py-1 text-xs text-slate-400">
                  {t}
                </span>
              ))}
            </div>
          </motion.section>
        )}

        {/* Trailer */}
        {anime.trailer?.site === "youtube" && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="mt-8"
          >
            <h2 className="mb-2 text-lg font-bold text-white">Trailer</h2>
            <div className="aspect-video w-full overflow-hidden rounded-2xl border border-white/8">
              <iframe
                src={`https://www.youtube.com/embed/${anime.trailer.id}`}
                title="Trailer"
                allowFullScreen
                className="h-full w-full"
              />
            </div>
          </motion.section>
        )}

        {/* Characters */}
        {anime.characters.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.25 }}
            className="mt-8"
          >
            <h2 className="mb-3 text-lg font-bold text-white">Characters</h2>
            <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-8">
              {anime.characters.map((c) => (
                <div key={c.name} className="flex flex-col items-center gap-1.5 text-center">
                  <div className="relative aspect-square w-full overflow-hidden rounded-xl border border-white/8 bg-slate-900">
                    {c.image && <Image src={c.image} alt={c.name} fill className="object-cover" />}
                  </div>
                  <p className="line-clamp-2 text-xs text-slate-400">{c.name}</p>
                </div>
              ))}
            </div>
          </motion.section>
        )}

        {/* More like this */}
        {similar && similar.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
            className="mt-10"
          >
            <h2 className="mb-3 text-lg font-bold text-white">More like this</h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {similar.map((a, i) => (
                <AnimeCard key={a.anilist_id} anime={a} index={i} />
              ))}
            </div>
          </motion.section>
        )}
      </div>
    </main>
  );
}
