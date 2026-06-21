"use client";

import { useMutation } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";

export interface AnimeRecommendation {
  anilist_id: number;
  title: string;
  title_romaji?: string;
  synopsis: string;
  genres: string[];
  tags: string[];
  year?: number;
  format?: string;
  mean_score?: number;
  episodes?: number;
  cover_image?: string;
  recommended_because: string;
  similarity: number;
}

export interface RecommendRequest {
  genres: string[];
  mood: string;
  themes: string[];
  era: string;
  length: string;
  loved_titles: string[];
}

export interface RecommendResponse {
  recommendations: AnimeRecommendation[];
  query_used: string;
  total_candidates: number;
  personalized: boolean;
}

async function fetchRecommendations(prefs: RecommendRequest): Promise<RecommendResponse> {
  const res = await fetch(`${BACKEND_URL}/api/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(prefs),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? "Failed to fetch recommendations");
  }
  return res.json();
}

export function useRecommendations() {
  return useMutation<RecommendResponse, Error, RecommendRequest>({
    mutationFn: fetchRecommendations,
  });
}
