"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";

async function fetchFeedback(): Promise<Record<string, number>> {
  const res = await fetch(`${BACKEND_URL}/api/feedback`, { credentials: "include" });
  if (!res.ok) return {};
  return res.json();
}

async function postFeedback({ anilist_id, signal }: { anilist_id: number; signal: number }): Promise<void> {
  const res = await fetch(`${BACKEND_URL}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ anilist_id, signal }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to save feedback" }));
    throw new Error(err.detail ?? "Failed to save feedback");
  }
}

export function useFeedback() {
  const { data: user } = useAniListUser();
  return useQuery<Record<string, number>>({
    queryKey: ["feedback"],
    queryFn: fetchFeedback,
    enabled: !!user,
    staleTime: 60 * 1000,
  });
}

export function useSetFeedback() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: postFeedback,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["feedback"] }),
  });
}
