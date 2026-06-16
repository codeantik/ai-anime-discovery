import { create } from "zustand";

export interface PreferencesState {
  genres: string[];
  mood: string;
  themes: string[];
  era: string;
  length: string;
  lovedTitles: string[];
  setField: <K extends keyof Omit<PreferencesState, "setField" | "reset">>(
    key: K,
    value: PreferencesState[K],
  ) => void;
  reset: () => void;
}

const initialState = {
  genres: [],
  mood: "",
  themes: [],
  era: "",
  length: "",
  lovedTitles: [],
};

export const usePreferencesStore = create<PreferencesState>((set) => ({
  ...initialState,
  setField: (key, value) => set({ [key]: value }),
  reset: () => set(initialState),
}));
