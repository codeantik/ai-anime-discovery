"use client";

import { motion } from "framer-motion";
import { Sparkles, Zap, ArrowRight } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (delay = 0) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      delay,
      ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
    },
  }),
};

export default function Home() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-4">
      {/* Background orbs */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute left-1/4 top-1/4 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-purple-600/20 blur-3xl" />
        <div className="absolute right-1/4 top-2/3 h-80 w-80 translate-x-1/2 rounded-full bg-indigo-500/15 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-pink-500/10 blur-3xl" />
      </div>

      <div className="flex max-w-3xl flex-col items-center gap-6 text-center">
        {/* Badge */}
        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={0}>
          <span className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-4 py-1.5 text-sm font-medium text-purple-300">
            <Sparkles className="h-3.5 w-3.5" />
            AI-Powered Anime Discovery
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          className="text-5xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl"
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={0.1}
        >
          Find anime you&apos;ll{" "}
          <span className="bg-gradient-to-r from-purple-400 via-indigo-400 to-pink-400 bg-clip-text text-transparent">
            actually love
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          className="max-w-xl text-lg text-slate-400 sm:text-xl"
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={0.2}
        >
          Tell us your vibe — we&apos;ll match you with titles that fit your taste, not just
          what&apos;s trending.
        </motion.p>

        {/* CTAs */}
        <motion.div
          className="flex flex-col items-center gap-3 sm:flex-row"
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={0.3}
        >
          <Link href="/discover"
            className="group inline-flex items-center rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-3 text-base font-semibold text-white shadow-lg shadow-purple-900/40 transition-all hover:from-purple-500 hover:to-indigo-500 hover:shadow-purple-900/60"
          >
            Start Discovering
            <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <Button variant="ghost" size="lg" className="rounded-full text-slate-400 hover:text-white">
            <Zap className="mr-2 h-4 w-4 text-yellow-400" />
            How it works
          </Button>
        </motion.div>

        {/* Stats */}
        <motion.div
          className="mt-4 flex gap-8 text-center"
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={0.4}
        >
          {[
            { value: "5000+", label: "Anime indexed" },
            { value: "AI", label: "Re-ranked picks" },
            { value: "Free", label: "Always" },
          ].map(({ value, label }) => (
            <div key={label}>
              <p className="text-2xl font-bold text-white">{value}</p>
              <p className="text-sm text-slate-500">{label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </main>
  );
}
