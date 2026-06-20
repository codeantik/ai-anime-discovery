"use client";

import { useQuery } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";

async function fetchSimilar(anilistId: number): Promise<AnimeRecommendation[]> {
  const res = await fetch(`${BACKEND_URL}/api/anime/${anilistId}/similar`);
  if (!res.ok) return [];
  return res.json();
}

export function useSimilarAnime(anilistId: number) {
  return useQuery<AnimeRecommendation[], Error>({
    queryKey: ["similar-anime", anilistId],
    queryFn: () => fetchSimilar(anilistId),
    staleTime: 10 * 60 * 1000,
    enabled: Number.isFinite(anilistId),
  });
}
