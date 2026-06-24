"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { AnimeRecommendation } from "@/lib/hooks/useRecommendations";

export interface DuoResponse {
  combined: boolean;
  recommendations: AnimeRecommendation[];
}

async function createDuoInvite(): Promise<{ token: string }> {
  const res = await fetch(`${BACKEND_URL}/api/duo/invite`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to create invite link" }));
    throw new Error(err.detail ?? "Failed to create invite link");
  }
  return res.json();
}

async function fetchDuo(token: string): Promise<DuoResponse> {
  const res = await fetch(`${BACKEND_URL}/api/duo/${token}`, { credentials: "include" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "This invite link is invalid or has expired." }));
    throw new Error(err.detail ?? "This invite link is invalid or has expired.");
  }
  return res.json();
}

export function useCreateDuoInvite() {
  return useMutation({ mutationFn: createDuoInvite });
}

export function useDuoRecommendations(token: string) {
  return useQuery<DuoResponse>({
    queryKey: ["duo", token],
    queryFn: () => fetchDuo(token),
    enabled: !!token,
    retry: false,
  });
}
