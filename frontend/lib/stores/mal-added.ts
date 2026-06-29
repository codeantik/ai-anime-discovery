import { create } from "zustand";

interface MALAddedState {
  addedIds: Set<number>;
  addId: (id: number) => void;
}

export const useMALAddedStore = create<MALAddedState>((set) => ({
  addedIds: new Set(),
  addId: (id: number) => set((state) => ({ addedIds: new Set([...state.addedIds, id]) })),
}));
