"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";

export type WatchlistSort = "added" | "taste";

async function fetchWatchlist(sort: WatchlistSort): Promise<AnimeRecommendation[]> {
  const res = await fetch(`${BACKEND_URL}/api/watchlist?sort=${sort}`, { credentials: "include" });
  if (!res.ok) return [];
  return res.json();
}

async function addToWatchlist(anilist_id: number): Promise<void> {
  const res = await fetch(`${BACKEND_URL}/api/watchlist/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ anilist_id }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to add to watchlist" }));
    throw new Error(err.detail ?? "Failed to add to watchlist");
  }
}

async function removeFromWatchlist(anilist_id: number): Promise<void> {
  const res = await fetch(`${BACKEND_URL}/api/watchlist/${anilist_id}`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to remove from watchlist" }));
    throw new Error(err.detail ?? "Failed to remove from watchlist");
  }
}

export function useWatchlist(sort: WatchlistSort = "added") {
  const { data: user } = useAniListUser();
  return useQuery<AnimeRecommendation[]>({
    queryKey: ["watchlist", sort],
    queryFn: () => fetchWatchlist(sort),
    enabled: !!user,
    staleTime: 60 * 1000,
  });
}

export function useAddToWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: addToWatchlist,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["watchlist"] }),
  });
}

export function useRemoveFromWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: removeFromWatchlist,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["watchlist"] }),
  });
}
