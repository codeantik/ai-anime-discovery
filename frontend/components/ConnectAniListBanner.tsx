"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Sparkles, X } from "lucide-react";
import { useState } from "react";
import { BACKEND_URL } from "@/lib/backendUrl";

export function ConnectAniListBanner() {
  const [dismissed, setDismissed] = useState(false);

  return (
    <AnimatePresence>
      {!dismissed && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="mb-6 flex flex-wrap items-center gap-3 rounded-2xl border border-teal-500/30 bg-teal-500/10 px-4 py-3 text-sm text-teal-300"
        >
          <Sparkles className="h-4 w-4 shrink-0" />
          <p className="flex-1">
            These picks are general — connect AniList so we can tailor them to your taste.
          </p>
          <a
            href={`${BACKEND_URL}/auth/anilist/login`}
            className="shrink-0 rounded-full border border-teal-500/30 bg-teal-500/10 px-3 py-1 font-medium transition-colors hover:border-teal-400/50 hover:bg-teal-500/20"
          >
            Connect AniList
          </a>
          <button
            onClick={() => setDismissed(true)}
            aria-label="Dismiss"
            className="shrink-0 cursor-pointer rounded-full p-1 text-teal-300/60 transition-colors hover:text-teal-300"
          >
            <X className="h-4 w-4" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
