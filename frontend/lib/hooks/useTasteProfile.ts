"use client";

import { useQuery } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";

export interface TasteProfileItem {
  name: string;
  weight: number;
}

export interface TasteProfileResponse {
  available: boolean;
  genres: TasteProfileItem[];
  tags: TasteProfileItem[];
}

async function fetchTasteProfile(): Promise<TasteProfileResponse> {
  const res = await fetch(`${BACKEND_URL}/api/taste/profile`, { credentials: "include" });
  if (!res.ok) return { available: false, genres: [], tags: [] };
  return res.json();
}

export function useTasteProfile() {
  const { data: user } = useAniListUser();
  return useQuery<TasteProfileResponse>({
    queryKey: ["taste-profile"],
    queryFn: fetchTasteProfile,
    enabled: !!user,
    staleTime: 5 * 60 * 1000,
  });
}
