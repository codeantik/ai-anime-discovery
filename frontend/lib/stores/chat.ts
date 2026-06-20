import { create } from "zustand";
import { ChatRecommendation } from "@/lib/hooks/useChat";

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  recommendations?: ChatRecommendation[];
}

export interface ChatState {
  turns: ChatTurn[];
  addTurn: (turn: ChatTurn) => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  turns: [],
  addTurn: (turn) => set((s) => ({ turns: [...s.turns, turn] })),
  reset: () => set({ turns: [] }),
}));
