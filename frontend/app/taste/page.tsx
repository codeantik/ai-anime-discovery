"use client";

import { motion } from "framer-motion";
import { Loader2, PieChart } from "lucide-react";
import { BACKEND_URL } from "@/lib/backendUrl";
import { useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useTasteProfile, type TasteProfileItem } from "@/lib/hooks/useTasteProfile";

const BAR_COLORS = ["from-purple-400 to-pink-400", "from-indigo-400 to-purple-400", "from-pink-400 to-rose-400"];

function TasteBarList({ items, colorOffset }: { items: TasteProfileItem[]; colorOffset: number }) {
  const max = items[0]?.weight ?? 1;
  return (
    <div className="flex flex-col gap-3">
      {items.map((item, i) => (
        <div key={item.name}>
          <div className="mb-1 flex items-baseline justify-between gap-2">
            <span className="truncate text-sm font-medium text-slate-200">{item.name}</span>
            <span className="shrink-0 text-xs text-slate-500">{Math.round(item.weight * 100)}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(item.weight / max) * 100}%` }}
              transition={{ duration: 0.6, delay: i * 0.04, ease: "easeOut" }}
              className={`h-full rounded-full bg-gradient-to-r ${BAR_COLORS[(i + colorOffset) % BAR_COLORS.length]}`}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function TasteProfilePage() {
  const { data: user, isLoading: userLoading } = useAniListUser();
  const { data: profile, isLoading: profileLoading } = useTasteProfile();

  if (userLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-[70vh] flex-col items-center justify-center gap-4 px-4 text-center">
        <PieChart className="h-10 w-10 text-purple-400/60" />
        <p className="max-w-sm text-slate-400">
          Connect your AniList account to see a breakdown of your taste in genres and tags.
        </p>
        <motion.a
          href={`${BACKEND_URL}/auth/anilist/login`}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className="inline-flex items-center gap-2 rounded-full border border-teal-500/30 bg-teal-500/10 px-4 py-1.5 text-sm font-medium text-teal-300 transition-colors hover:border-teal-400/50 hover:bg-teal-500/20"
        >
          Connect AniList
        </motion.a>
      </main>
    );
  }

  if (profileLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-4xl px-4 pb-20 pt-8">
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-2xl font-bold text-white">
          Your{" "}
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Taste Profile
          </span>
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Built from your AniList history and feedback — the same signal that drives your recommendations.
        </p>
      </motion.div>

      {!profile?.available ? (
        <div className="flex flex-col items-center gap-2 py-16 text-center text-slate-500">
          <PieChart className="h-8 w-8 text-slate-700" />
          Not enough taste signal yet — rate a few anime or sync your AniList history to unlock your
          profile.
        </div>
      ) : (
        <div className="grid gap-8 sm:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur"
          >
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
              Top Genres
            </h2>
            <TasteBarList items={profile.genres} colorOffset={0} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur"
          >
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
              Top Tags
            </h2>
            <TasteBarList items={profile.tags} colorOffset={1} />
          </motion.div>
        </div>
      )}
    </main>
  );
}
