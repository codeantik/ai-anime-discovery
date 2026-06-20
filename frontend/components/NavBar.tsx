"use client";

import { motion } from "framer-motion";
import { LogOut, Sparkles, User } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { BACKEND_URL } from "@/lib/backendUrl";
import { useAniListLogout, useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useMALLogout, useMALUser } from "@/lib/hooks/useMALAuth";

export function NavBar() {
  const { data: user, isLoading } = useAniListUser();
  const { mutate: logout, isPending: loggingOut } = useAniListLogout();
  const { data: malUser, isLoading: malLoading } = useMALUser();
  const { mutate: malLogout, isPending: malLoggingOut } = useMALLogout();

  return (
    <nav className="sticky top-0 z-50 border-b border-white/6 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-y-2 gap-x-3 px-3 py-2 sm:px-4 sm:py-3">
        <Link href="/" className="flex items-center gap-2 font-bold text-white">
          <Sparkles className="h-5 w-5 text-purple-400" />
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            AniDiscover
          </span>
        </Link>

        <div className="flex flex-1 flex-wrap items-center justify-end gap-2 sm:gap-4">
          <Link href="/discover" className="text-sm text-slate-400 transition-colors hover:text-white">
            Discover
          </Link>

          {!isLoading && (
            <>
              {user ? (
                <div className="flex items-center gap-1.5 sm:gap-3">
                  <div className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-2 py-1 sm:gap-2 sm:px-3 sm:py-1.5">
                    {user.picture ? (
                      <Image src={user.picture} alt={user.name} width={20} height={20} className="rounded-full" />
                    ) : (
                      <User className="h-4 w-4 text-purple-400" />
                    )}
                    <span className="hidden max-w-[8rem] truncate text-sm text-slate-300 sm:inline">
                      {user.name}
                    </span>
                  </div>
                  <button
                    onClick={() => logout()}
                    disabled={loggingOut}
                    title="Disconnect AniList"
                    className="flex items-center gap-1.5 rounded-full px-2 py-1 text-sm text-slate-500 transition-colors hover:text-red-400 sm:px-3 sm:py-1.5"
                  >
                    <LogOut className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline">Disconnect</span>
                  </button>
                </div>
              ) : (
                <motion.a
                  href={`${BACKEND_URL}/auth/anilist/login`}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="inline-flex items-center gap-1.5 rounded-full border border-teal-500/30 bg-teal-500/10 px-2.5 py-1 text-xs font-medium text-teal-300 transition-colors hover:border-teal-400/50 hover:bg-teal-500/20 sm:gap-2 sm:px-4 sm:py-1.5 sm:text-sm"
                >
                  <svg className="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6.361 2.943 0 21.056h4.942l1.077-3.133H11.4l1.08 3.133H17.5L11.139 2.943zM7.241 14.03l1.97-5.735 1.964 5.735zm9.994 4.855-.78-2.26c1.5-.55 2.45-1.77 2.45-3.25 0-2.1-1.67-3.38-4.39-3.38h-1v2.24h.73c1.32 0 2.12.56 2.12 1.54 0 .92-.7 1.51-1.85 1.57l.87 2.52z" />
                  </svg>
                  <span className="hidden sm:inline">Connect </span>AniList
                </motion.a>
              )}
            </>
          )}

          {!malLoading && (
            <>
              {malUser ? (
                <div className="flex items-center gap-1.5 sm:gap-3">
                  <div className="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-2 py-1 sm:gap-2 sm:px-3 sm:py-1.5">
                    {malUser.picture ? (
                      <Image src={malUser.picture} alt={malUser.name} width={20} height={20} className="rounded-full" />
                    ) : (
                      <User className="h-4 w-4 text-blue-400" />
                    )}
                    <span className="hidden max-w-[8rem] truncate text-sm text-slate-300 sm:inline">
                      {malUser.name}
                    </span>
                  </div>
                  <button
                    onClick={() => malLogout()}
                    disabled={malLoggingOut}
                    title="Disconnect MAL"
                    className="flex items-center gap-1.5 rounded-full px-2 py-1 text-sm text-slate-500 transition-colors hover:text-red-400 sm:px-3 sm:py-1.5"
                  >
                    <LogOut className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline">Disconnect</span>
                  </button>
                </div>
              ) : (
                <motion.a
                  href={`${BACKEND_URL}/auth/mal/login`}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="inline-flex items-center gap-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 px-2.5 py-1 text-xs font-medium text-blue-300 transition-colors hover:border-blue-400/50 hover:bg-blue-500/20 sm:gap-2 sm:px-4 sm:py-1.5 sm:text-sm"
                >
                  <span className="hidden sm:inline">Connect </span>MAL
                </motion.a>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
