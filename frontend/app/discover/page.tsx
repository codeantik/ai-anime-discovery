"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ConnectAniListBanner } from "@/components/ConnectAniListBanner";
import { PreferencesForm } from "@/components/PreferencesForm";
import { ResultsGrid } from "@/components/ResultsGrid";
import { useRecommendations, RecommendRequest } from "@/lib/hooks/useRecommendations";
import { useResultsStore } from "@/lib/stores/results";

export default function DiscoverPage() {
  const { mutate, isPending, error, reset: resetMutation } = useRecommendations();
  const { data, setData } = useResultsStore();

  const handleSubmit = (prefs: RecommendRequest) => mutate(prefs, { onSuccess: setData });
  const reset = () => {
    setData(null);
    resetMutation();
  };

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-16">
      {/* Background orbs */}
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute left-1/4 top-0 h-[40rem] w-[40rem] -translate-x-1/2 rounded-full bg-purple-700/15 blur-3xl" />
        <div className="absolute right-0 top-1/2 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl" />
      </div>

      <div className="mx-auto max-w-6xl">
        {/* Page title */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 text-center"
        >
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            {data ? "Your recommendations" : "Discover your next"}
            {!data && (
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {" "}obsession
              </span>
            )}
          </h1>
          {!data && (
            <p className="mt-3 text-slate-500">Answer 4 quick questions and we&apos;ll find your perfect match.</p>
          )}
        </motion.div>

        <AnimatePresence mode="wait">
          {/* Error state */}
          {error && !isPending && (
            <motion.div key="error"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="mb-6 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300"
            >
              {error.message}
              <button onClick={reset} className="ml-3 cursor-pointer underline opacity-70 hover:opacity-100">Try again</button>
            </motion.div>
          )}

          {/* Results */}
          {data && !isPending ? (
            <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              {data.recommendations.length === 0 ? (
                <div className="py-20 text-center text-slate-500">
                  No matches found. Try loosening your filters.
                  <button onClick={reset} className="ml-2 cursor-pointer text-purple-400 underline">Start over</button>
                </div>
              ) : (
                <>
                  {!data.personalized && <ConnectAniListBanner />}
                  <ResultsGrid
                    recommendations={data.recommendations}
                    queryUsed={data.query_used}
                    onReset={reset}
                  />
                </>
              )}
            </motion.div>
          ) : (
            /* Form */
            <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex justify-center"
            >
              <PreferencesForm onSubmit={handleSubmit} isLoading={isPending} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
