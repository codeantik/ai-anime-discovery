import { create } from "zustand";
import { RecommendResponse } from "@/lib/hooks/useRecommendations";

export interface ResultsState {
  data: RecommendResponse | null;
  setData: (data: RecommendResponse | null) => void;
}

export const useResultsStore = create<ResultsState>((set) => ({
  data: null,
  setData: (data) => set({ data }),
}));
