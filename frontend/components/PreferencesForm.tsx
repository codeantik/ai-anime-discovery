"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Sparkles, X } from "lucide-react";
import { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { RecommendRequest } from "@/lib/hooks/useRecommendations";

// ── Static option lists ────────────────────────────────────────────────────

const GENRES = [
  "Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror",
  "Mystery", "Psychological", "Romance", "Sci-Fi", "Slice of Life",
  "Sports", "Supernatural", "Thriller", "Mecha", "Music", "Historical",
];

const MOODS = [
  { label: "Wholesome & cozy",      emoji: "🌸" },
  { label: "Epic & thrilling",       emoji: "⚡" },
  { label: "Dark & gritty",          emoji: "🖤" },
  { label: "Funny & lighthearted",   emoji: "😂" },
  { label: "Emotional & tearjerking",emoji: "😭" },
  { label: "Mind-bending",           emoji: "🌀" },
  { label: "Romantic",               emoji: "💜" },
  { label: "Scary & creepy",         emoji: "👻" },
];

const THEMES = [
  "School", "Isekai", "Time Travel", "Superpowers", "Military",
  "Space", "Cooking", "Music & Art", "Sports", "Friendship",
  "Family", "Survival", "Detective", "Magic", "Revenge",
];

const ERAS = [
  { label: "Any era",       value: "any" },
  { label: "Classic (pre-2000)", value: "classic" },
  { label: "2000s",         value: "2000s" },
  { label: "2010s",         value: "2010s" },
  { label: "Recent (2020+)", value: "recent" },
];

const LENGTHS = [
  { label: "Any length",    value: "any" },
  { label: "Movie",         value: "movie" },
  { label: "Short (≤13 ep)", value: "short" },
  { label: "Season (13-26)", value: "season" },
  { label: "Long (26+ ep)", value: "long" },
];

// ── Sub-components ─────────────────────────────────────────────────────────

function Chip({
  label, selected, onClick,
}: { label: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-4 py-1.5 text-sm font-medium transition-all duration-200
        ${selected
          ? "border-purple-500 bg-purple-500/20 text-purple-200 shadow-[0_0_12px_rgba(168,85,247,0.3)]"
          : "border-white/10 bg-white/5 text-slate-400 hover:border-white/30 hover:text-white"
        }`}
    >
      {label}
    </button>
  );
}

function PillButton({
  label, selected, onClick,
}: { label: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl border px-5 py-2 text-sm font-medium transition-all duration-200
        ${selected
          ? "border-indigo-500 bg-indigo-500/20 text-indigo-200"
          : "border-white/10 bg-white/5 text-slate-400 hover:border-white/30 hover:text-white"
        }`}
    >
      {label}
    </button>
  );
}

// ── Steps ──────────────────────────────────────────────────────────────────

const STEPS = [
  { title: "What genres do you love?",   subtitle: "Pick as many as you want" },
  { title: "What's your vibe?",          subtitle: "Choose a mood and any themes" },
  { title: "Any preferences?",           subtitle: "Filter by era or episode count" },
  { title: "What have you loved?",       subtitle: "Optional — helps us personalise your picks" },
];

// ── Main form ──────────────────────────────────────────────────────────────

interface Props {
  onSubmit: (prefs: RecommendRequest) => void;
  isLoading: boolean;
}

export function PreferencesForm({ onSubmit, isLoading }: Props) {
  const [step, setStep] = useState(0);
  const [genres, setGenres] = useState<string[]>([]);
  const [mood, setMood] = useState("");
  const [themes, setThemes] = useState<string[]>([]);
  const [era, setEra] = useState("any");
  const [length, setLength] = useState("any");
  const [lovedTitles, setLovedTitles] = useState<string[]>([]);
  const [titleInput, setTitleInput] = useState("");

  const toggle = <T,>(arr: T[], val: T): T[] =>
    arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val];

  const addTitle = () => {
    const v = titleInput.trim();
    if (v && !lovedTitles.includes(v)) setLovedTitles((prev) => [...prev, v]);
    setTitleInput("");
  };

  const handleTitleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") { e.preventDefault(); addTitle(); }
    if (e.key === "Backspace" && !titleInput && lovedTitles.length > 0)
      setLovedTitles((prev) => prev.slice(0, -1));
  };

  const handleSubmit = () => {
    onSubmit({ genres, mood, themes, era, length, loved_titles: lovedTitles });
  };

  const canNext = step === 0 ? genres.length > 0 : true;

  const slideVariants = {
    enter: (dir: number) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit:  (dir: number) => ({ x: dir > 0 ? -60 : 60, opacity: 0 }),
  };

  const [dir, setDir] = useState(1);
  const go = (next: number) => { setDir(next > step ? 1 : -1); setStep(next); };

  return (
    <div className="w-full max-w-2xl">
      {/* Progress bar */}
      <div className="mb-8 flex gap-2">
        {STEPS.map((_, i) => (
          <div
            key={i}
            className={`h-1 flex-1 rounded-full transition-all duration-500 ${
              i <= step ? "bg-purple-500" : "bg-white/10"
            }`}
          />
        ))}
      </div>

      <AnimatePresence mode="wait" custom={dir}>
        <motion.div
          key={step}
          custom={dir}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
        >
          {/* Step header */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white">{STEPS[step].title}</h2>
            <p className="mt-1 text-sm text-slate-500">{STEPS[step].subtitle}</p>
          </div>

          {/* Step 0 — Genres */}
          {step === 0 && (
            <div className="flex flex-wrap gap-2">
              {GENRES.map((g) => (
                <Chip key={g} label={g} selected={genres.includes(g)}
                  onClick={() => setGenres(toggle(genres, g))} />
              ))}
            </div>
          )}

          {/* Step 1 — Mood + Themes */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {MOODS.map(({ label, emoji }) => (
                  <button key={label} type="button" onClick={() => setMood(mood === label ? "" : label)}
                    className={`flex flex-col items-center gap-1 rounded-2xl border p-4 text-center transition-all duration-200
                      ${mood === label
                        ? "border-pink-500/60 bg-pink-500/15 shadow-[0_0_16px_rgba(236,72,153,0.2)]"
                        : "border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10"
                      }`}
                  >
                    <span className="text-2xl">{emoji}</span>
                    <span className="text-xs font-medium text-slate-300">{label}</span>
                  </button>
                ))}
              </div>
              <div>
                <p className="mb-2 text-xs font-medium uppercase tracking-widest text-slate-500">Themes</p>
                <div className="flex flex-wrap gap-2">
                  {THEMES.map((t) => (
                    <Chip key={t} label={t} selected={themes.includes(t)}
                      onClick={() => setThemes(toggle(themes, t))} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 2 — Era + Length */}
          {step === 2 && (
            <div className="space-y-8">
              <div>
                <p className="mb-3 text-xs font-medium uppercase tracking-widest text-slate-500">Era</p>
                <div className="flex flex-wrap gap-2">
                  {ERAS.map(({ label, value }) => (
                    <PillButton key={value} label={label} selected={era === value}
                      onClick={() => setEra(value)} />
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-3 text-xs font-medium uppercase tracking-widest text-slate-500">Length</p>
                <div className="flex flex-wrap gap-2">
                  {LENGTHS.map(({ label, value }) => (
                    <PillButton key={value} label={label} selected={length === value}
                      onClick={() => setLength(value)} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3 — Loved Titles */}
          {step === 3 && (
            <div className="space-y-4">
              <div className="flex min-h-[3rem] flex-wrap items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-3">
                {lovedTitles.map((t) => (
                  <span key={t} className="flex items-center gap-1 rounded-full bg-purple-500/20 px-3 py-1 text-sm text-purple-200">
                    {t}
                    <button onClick={() => setLovedTitles((prev) => prev.filter((x) => x !== t))}>
                      <X className="h-3 w-3 opacity-60 hover:opacity-100" />
                    </button>
                  </span>
                ))}
                <input
                  value={titleInput}
                  onChange={(e) => setTitleInput(e.target.value)}
                  onKeyDown={handleTitleKey}
                  onBlur={addTitle}
                  placeholder={lovedTitles.length === 0 ? "Type an anime title, press Enter…" : "Add another…"}
                  className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600 min-w-[180px]"
                />
              </div>
              <p className="text-xs text-slate-600">Press Enter or comma to add. Backspace to remove.</p>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="mt-10 flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => go(step - 1)}
          className={`text-slate-500 ${step === 0 ? "invisible" : ""}`}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Back
        </Button>

        {step < STEPS.length - 1 ? (
          <Button onClick={() => go(step + 1)} disabled={!canNext}
            className="rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-6 font-semibold text-white hover:from-purple-500 hover:to-indigo-500 disabled:opacity-40">
            Next <ArrowRight className="ml-1 h-4 w-4" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={isLoading}
            className="group rounded-full bg-gradient-to-r from-purple-600 to-pink-600 px-8 font-semibold text-white shadow-lg shadow-purple-900/40 hover:from-purple-500 hover:to-pink-500 disabled:opacity-60">
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Finding your picks…
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" /> Get Recommendations
              </span>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
