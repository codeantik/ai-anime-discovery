"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export interface MALUser {
  id: number;
  name: string;
  picture?: string;
}

async function fetchMALUser(): Promise<MALUser | null> {
  const res = await fetch("/api/backend/auth/mal/me", { credentials: "include" });
  if (res.status === 401) return null;
  if (!res.ok) return null;
  return res.json();
}

async function logoutMAL(): Promise<void> {
  await fetch("/api/backend/auth/mal/logout", {
    method: "POST",
    credentials: "include",
  });
}

async function addToMAL(anilist_id: number, status = "plan_to_watch"): Promise<{ status: string; mal_id: number }> {
  const res = await fetch("/api/backend/mal/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ anilist_id, status }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to add to MAL" }));
    throw new Error(err.detail ?? "Failed to add to MAL");
  }
  return res.json();
}

export function useMALUser() {
  return useQuery<MALUser | null>({
    queryKey: ["mal-user"],
    queryFn: fetchMALUser,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useMALLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: logoutMAL,
    onSuccess: () => queryClient.setQueryData(["mal-user"], null),
  });
}

export function useAddToMAL() {
  return useMutation({
    mutationFn: ({ anilist_id, status }: { anilist_id: number; status?: string }) =>
      addToMAL(anilist_id, status),
  });
}
