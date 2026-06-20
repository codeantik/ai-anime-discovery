"use client";

import { useMutation } from "@tanstack/react-query";
import { BACKEND_URL } from "@/lib/backendUrl";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRecommendation {
  anilist_id: number;
  title: string;
  year?: number;
  genres: string[];
  recommended_because: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
}

export interface ChatResponse {
  reply: string;
  recommendations: ChatRecommendation[];
}

async function postChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? "Chat request failed");
  }
  return res.json();
}

export function useChat() {
  return useMutation<ChatResponse, Error, ChatRequest>({
    mutationFn: postChat,
  });
}
