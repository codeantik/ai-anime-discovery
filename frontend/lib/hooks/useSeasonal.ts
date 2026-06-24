"use client";

import { useQuery } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";

export interface SeasonalResponse {
  season: string;
  year: number;
  anime: AnimeRecommendation[];
  personalized: boolean;
}

async function fetchSeasonal(): Promise<SeasonalResponse> {
  const res = await fetch(`${BACKEND_URL}/api/seasonal`, { credentials: "include" });
  if (!res.ok) return { season: "", year: 0, anime: [], personalized: false };
  return res.json();
}

export function useSeasonal() {
  return useQuery<SeasonalResponse>({
    queryKey: ["seasonal"],
    queryFn: fetchSeasonal,
    staleTime: 5 * 60 * 1000,
  });
}
