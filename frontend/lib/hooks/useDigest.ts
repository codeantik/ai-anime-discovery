"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";

export interface DigestResponse {
  available: boolean;
  recommendations: AnimeRecommendation[];
  generated_at: string | null;
  viewed: boolean;
}

async function fetchDigest(): Promise<DigestResponse> {
  const res = await fetch(`${BACKEND_URL}/api/digest`, { credentials: "include" });
  if (!res.ok) return { available: false, recommendations: [], generated_at: null, viewed: true };
  return res.json();
}

async function markDigestViewed(): Promise<void> {
  await fetch(`${BACKEND_URL}/api/digest/viewed`, { method: "POST", credentials: "include" });
}

export function useDigest() {
  const { data: user } = useAniListUser();
  return useQuery<DigestResponse>({
    queryKey: ["digest"],
    queryFn: fetchDigest,
    enabled: !!user,
    staleTime: 5 * 60 * 1000,
  });
}

export function useMarkDigestViewed() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markDigestViewed,
    onSuccess: () =>
      queryClient.setQueryData<DigestResponse | undefined>(["digest"], (prev) =>
        prev ? { ...prev, viewed: true } : prev
      ),
  });
}
