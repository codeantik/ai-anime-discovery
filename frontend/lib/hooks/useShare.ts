"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";

interface SharedResponse {
  type: "card" | "watchlist" | "digest";
  anime: AnimeRecommendation[];
  generated_at?: string | null;
}

async function shareCard(args: { anilist_id: number; recommended_because?: string }): Promise<{ token: string }> {
  const res = await fetch(`${BACKEND_URL}/api/share/card`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(args),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to create share link" }));
    throw new Error(err.detail ?? "Failed to create share link");
  }
  return res.json();
}

async function shareWatchlist(): Promise<{ token: string }> {
  const res = await fetch(`${BACKEND_URL}/api/share/watchlist`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to create share link" }));
    throw new Error(err.detail ?? "Failed to create share link");
  }
  return res.json();
}

async function shareDigest(): Promise<{ token: string }> {
  const res = await fetch(`${BACKEND_URL}/api/share/digest`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to create share link" }));
    throw new Error(err.detail ?? "Failed to create share link");
  }
  return res.json();
}

async function fetchSharedContent(token: string): Promise<SharedResponse> {
  const res = await fetch(`${BACKEND_URL}/api/share/${token}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "This share link is invalid or has expired." }));
    throw new Error(err.detail ?? "This share link is invalid or has expired.");
  }
  return res.json();
}

export function useCreateCardShare() {
  return useMutation({ mutationFn: shareCard });
}

export function useCreateWatchlistShare() {
  return useMutation({ mutationFn: shareWatchlist });
}

export function useCreateDigestShare() {
  return useMutation({ mutationFn: shareDigest });
}

export function useSharedContent(token: string) {
  return useQuery<SharedResponse>({
    queryKey: ["share", token],
    queryFn: () => fetchSharedContent(token),
    enabled: !!token,
    retry: false,
  });
}
