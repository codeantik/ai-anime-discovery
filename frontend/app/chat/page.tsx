"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Send, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ChatMessage, useChat } from "@/lib/hooks/useChat";
import { useChatStore } from "@/lib/stores/chat";

export default function ChatPage() {
  const { turns, addTurn } = useChatStore();
  const { mutate, isPending, error } = useChat();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, isPending]);

  const send = () => {
    const text = input.trim();
    if (!text || isPending) return;

    const nextTurns = [...turns, { role: "user" as const, content: text }];
    addTurn({ role: "user", content: text });
    setInput("");

    const history: ChatMessage[] = nextTurns.map((t) => ({ role: t.role, content: t.content }));
    mutate(
      { messages: history },
      {
        onSuccess: (res) =>
          addTurn({ role: "assistant", content: res.reply, recommendations: res.recommendations }),
      },
    );
  };

  return (
    <main className="relative flex min-h-[calc(100vh-4rem)] flex-col overflow-hidden px-3 py-6 sm:px-4">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute left-1/4 top-0 h-[40rem] w-[40rem] -translate-x-1/2 rounded-full bg-purple-700/15 blur-3xl" />
        <div className="absolute right-0 top-1/2 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl" />
      </div>

      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-6 text-center">
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Chat with your{" "}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              anime guide
            </span>
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Tell it what you&apos;re in the mood for — it&apos;ll ask, search, and recommend.
          </p>
        </motion.div>

        <div className="flex-1 space-y-4 overflow-y-auto pb-4">
          {turns.length === 0 && !isPending && (
            <div className="rounded-2xl border border-white/8 bg-white/4 p-4 text-sm text-slate-400 backdrop-blur-md">
              <Sparkles className="mb-1.5 h-4 w-4 text-purple-400" />
              Try: &quot;I want something like Steins;Gate but shorter&quot; or &quot;what&apos;s a good
              chill slice-of-life airing right now?&quot;
            </div>
          )}

          <AnimatePresence initial={false}>
            {turns.map((turn, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${turn.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed backdrop-blur-md ${
                    turn.role === "user"
                      ? "bg-purple-600/80 text-white"
                      : "border border-white/8 bg-white/4 text-slate-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{turn.content}</p>

                  {turn.recommendations && turn.recommendations.length > 0 && (
                    <div className="mt-3 flex flex-col gap-2">
                      {turn.recommendations.map((rec, recIndex) => (
                        <button
                          key={`${rec.anilist_id}-${recIndex}`}
                          onClick={() => router.push(`/anime/${rec.anilist_id}`)}
                          className="cursor-pointer rounded-xl border border-white/8 bg-white/5 p-3 text-left transition-colors hover:border-purple-500/30 hover:bg-white/10"
                        >
                          <div className="flex flex-wrap items-baseline justify-between gap-1">
                            <span className="font-semibold text-white">{rec.title}</span>
                            {rec.year && <span className="text-xs text-slate-500">{rec.year}</span>}
                          </div>
                          {rec.genres.length > 0 && (
                            <div className="mt-1 flex flex-wrap gap-1">
                              {rec.genres.slice(0, 3).map((g) => (
                                <span
                                  key={g}
                                  className="rounded-full bg-indigo-500/15 px-2 py-0.5 text-xs text-indigo-300"
                                >
                                  {g}
                                </span>
                              ))}
                            </div>
                          )}
                          <p className="mt-1 text-xs text-slate-400">{rec.recommended_because}</p>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isPending && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="rounded-2xl border border-white/8 bg-white/4 px-4 py-3 text-sm text-slate-400 backdrop-blur-md">
                <span className="inline-flex gap-1">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-purple-400 [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-purple-400 [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-purple-400" />
                </span>
              </div>
            </motion.div>
          )}

          {error && !isPending && (
            <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
              {error.message}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="sticky bottom-0 flex items-center gap-2 border-t border-white/6 bg-slate-950/80 py-3 backdrop-blur-md">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask for a recommendation..."
            className="flex-1 rounded-full border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-purple-500/40"
          />
          <button
            onClick={send}
            disabled={isPending || !input.trim()}
            aria-label="Send message"
            className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white transition-opacity disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </main>
  );
}
