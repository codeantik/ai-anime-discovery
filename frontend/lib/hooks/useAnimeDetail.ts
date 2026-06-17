"use client";

import { useQuery } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";

export interface Character {
  name: string;
  image?: string;
}

export interface Trailer {
  site: string;
  id: string;
}

export interface AnimeDetail {
  anilist_id: number;
  title: string;
  title_romaji?: string;
  synopsis: string;
  genres: string[];
  tags: string[];
  year?: number;
  format?: string;
  status?: string;
  mean_score?: number;
  episodes?: number;
  duration?: number;
  source?: string;
  cover_image?: string;
  banner_image?: string;
  studios: string[];
  trailer?: Trailer;
  characters: Character[];
}

async function fetchAnimeDetail(anilistId: number): Promise<AnimeDetail> {
  const res = await fetch(`${BACKEND_URL}/api/anime/${anilistId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to load anime" }));
    throw new Error(err.detail ?? "Failed to load anime");
  }
  return res.json();
}

export function useAnimeDetail(anilistId: number) {
  return useQuery<AnimeDetail, Error>({
    queryKey: ["anime-detail", anilistId],
    queryFn: () => fetchAnimeDetail(anilistId),
    staleTime: 10 * 60 * 1000,
    enabled: Number.isFinite(anilistId),
  });
}
