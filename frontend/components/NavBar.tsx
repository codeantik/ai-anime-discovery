"use client";

import { motion } from "framer-motion";
import { LogOut, Sparkles, User } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useMALLogout, useMALUser } from "@/lib/hooks/useMALAuth";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8001";

export function NavBar() {
  const { data: user, isLoading } = useMALUser();
  const { mutate: logout, isPending: loggingOut } = useMALLogout();

  return (
    <nav className="fixed inset-x-0 top-0 z-50 border-b border-white/6 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-bold text-white">
          <Sparkles className="h-5 w-5 text-purple-400" />
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            AniDiscover
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-6">
          <Link href="/discover" className="text-sm text-slate-400 transition-colors hover:text-white">
            Discover
          </Link>

          {!isLoading && (
            <>
              {user ? (
                <div className="flex items-center gap-3">
                  {/* Avatar */}
                  <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5">
                    {user.picture ? (
                      <Image
                        src={user.picture}
                        alt={user.name}
                        width={20}
                        height={20}
                        className="rounded-full"
                      />
                    ) : (
                      <User className="h-4 w-4 text-purple-400" />
                    )}
                    <span className="text-sm text-slate-300">{user.name}</span>
                  </div>

                  {/* Logout */}
                  <button
                    onClick={() => logout()}
                    disabled={loggingOut}
                    className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm text-slate-500 transition-colors hover:text-red-400"
                  >
                    <LogOut className="h-3.5 w-3.5" />
                    Disconnect
                  </button>
                </div>
              ) : (
                <motion.a
                  href={`${BACKEND_URL}/auth/mal/login`}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm font-medium text-blue-300 transition-colors hover:border-blue-400/50 hover:bg-blue-500/20"
                >
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6.5 7h3.5v10H6.5z M10 7l4 5-4 5h3l4-5-4-5z" />
                  </svg>
                  Connect MAL
                </motion.a>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
