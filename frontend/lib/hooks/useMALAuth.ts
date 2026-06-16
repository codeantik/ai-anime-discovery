"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export interface AniListUser {
  id: number;
  name: string;
  picture?: string;
}

async function fetchAniListUser(): Promise<AniListUser | null> {
  const res = await fetch("/api/backend/auth/anilist/me", { credentials: "include" });
  if (res.status === 401) return null;
  if (!res.ok) return null;
  return res.json();
}

async function logoutAniList(): Promise<void> {
  await fetch("/api/backend/auth/anilist/logout", {
    method: "POST",
    credentials: "include",
  });
}

async function addToList(
  anilist_id: number,
  status = "PLANNING",
): Promise<{ status: string; anilist_id: number }> {
  const res = await fetch("/api/backend/list/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ anilist_id, status }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to add to list" }));
    throw new Error(err.detail ?? "Failed to add to list");
  }
  return res.json();
}

export function useAniListUser() {
  return useQuery<AniListUser | null>({
    queryKey: ["anilist-user"],
    queryFn: fetchAniListUser,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useAniListLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: logoutAniList,
    onSuccess: () => queryClient.setQueryData(["anilist-user"], null),
  });
}

export function useAddToList() {
  return useMutation({
    mutationFn: ({ anilist_id, status }: { anilist_id: number; status?: string }) =>
      addToList(anilist_id, status),
  });
}
