"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";

export interface GoogleUser {
  id: string;
  name: string;
  email?: string;
  picture?: string;
}

async function fetchGoogleUser(): Promise<GoogleUser | null> {
  const res = await fetch(`${BACKEND_URL}/auth/google/me`, { credentials: "include" });
  if (res.status === 401) return null;
  if (!res.ok) return null;
  return res.json();
}

async function logoutGoogle(): Promise<void> {
  await fetch(`${BACKEND_URL}/auth/google/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export function useGoogleUser() {
  return useQuery<GoogleUser | null>({
    queryKey: ["google-user"],
    queryFn: fetchGoogleUser,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useGoogleLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: logoutGoogle,
    onSuccess: () => queryClient.setQueryData(["google-user"], null),
  });
}
