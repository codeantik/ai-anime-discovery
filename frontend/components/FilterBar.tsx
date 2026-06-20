"use client";

import { Search, X } from "lucide-react";

export interface Filters {
  search: string;
  genre: string;
  format: string;
  minScore: number;
}

export const EMPTY_FILTERS: Filters = { search: "", genre: "", format: "", minScore: 0 };

interface Props {
  genres: string[];
  formats: string[];
  filters: Filters;
  onChange: (filters: Filters) => void;
}

const SELECT_CLASS =
  "rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-slate-300 outline-none transition-colors hover:border-white/20";

export function FilterBar({ genres, formats, filters, onChange }: Props) {
  const isActive = filters.search || filters.genre || filters.format || filters.minScore > 0;

  return (
    <div className="mb-6 flex flex-wrap items-center gap-2 rounded-2xl border border-white/8 bg-white/4 p-3 backdrop-blur-md">
      <div className="flex w-full min-w-0 flex-1 items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 sm:w-auto sm:min-w-[160px]">
        <Search className="h-3.5 w-3.5 shrink-0 text-slate-500" />
        <input
          value={filters.search}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
          placeholder="Search title…"
          className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
        />
      </div>

      <select
        value={filters.genre}
        onChange={(e) => onChange({ ...filters, genre: e.target.value })}
        style={{ colorScheme: "dark" }}
        className={SELECT_CLASS}
      >
        <option value="">All genres</option>
        {genres.map((g) => (
          <option key={g} value={g}>{g}</option>
        ))}
      </select>

      <select
        value={filters.format}
        onChange={(e) => onChange({ ...filters, format: e.target.value })}
        style={{ colorScheme: "dark" }}
        className={SELECT_CLASS}
      >
        <option value="">All formats</option>
        {formats.map((f) => (
          <option key={f} value={f}>{f}</option>
        ))}
      </select>

      <select
        value={filters.minScore}
        onChange={(e) => onChange({ ...filters, minScore: Number(e.target.value) })}
        style={{ colorScheme: "dark" }}
        className={SELECT_CLASS}
      >
        <option value={0}>Any score</option>
        <option value={70}>70+</option>
        <option value={80}>80+</option>
        <option value={90}>90+</option>
      </select>

      {isActive && (
        <button
          type="button"
          onClick={() => onChange(EMPTY_FILTERS)}
          className="flex items-center gap-1 rounded-full border border-white/10 px-3 py-1.5 text-xs text-slate-400 transition-colors hover:text-white"
        >
          <X className="h-3 w-3" /> Clear
        </button>
      )}
    </div>
  );
}
