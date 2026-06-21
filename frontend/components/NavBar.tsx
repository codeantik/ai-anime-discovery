"use client";

import { Popover } from "@base-ui/react/popover";
import { motion } from "framer-motion";
import { Bell, Bookmark, Compass, MessageCircle, Sparkles, User, X } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef } from "react";
import { BACKEND_URL } from "@/lib/backendUrl";
import { useAniListLogout, useAniListUser } from "@/lib/hooks/useAniListAuth";
import { useDigest } from "@/lib/hooks/useDigest";
import { useGoogleLogout, useGoogleUser } from "@/lib/hooks/useGoogleAuth";
import { useMALLogout, useMALUser } from "@/lib/hooks/useMALAuth";

const NAV_LINKS = [
  { href: "/discover", label: "Discover", icon: Compass },
  { href: "/chat", label: "Chat", icon: MessageCircle },
  { href: "/watchlist", label: "Watchlist", icon: Bookmark },
  { href: "/digest", label: "For You", icon: Bell },
];

type ConnectionAccent = "emerald" | "teal" | "blue";

const ACCENT_CLASSES: Record<ConnectionAccent, { border: string; bg: string; text: string; hoverBorder: string; hoverBg: string }> = {
  emerald: {
    border: "border-emerald-500/30",
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
    hoverBorder: "hover:border-emerald-400/50",
    hoverBg: "hover:bg-emerald-500/20",
  },
  teal: {
    border: "border-teal-500/30",
    bg: "bg-teal-500/10",
    text: "text-teal-300",
    hoverBorder: "hover:border-teal-400/50",
    hoverBg: "hover:bg-teal-500/20",
  },
  blue: {
    border: "border-blue-500/30",
    bg: "bg-blue-500/10",
    text: "text-blue-300",
    hoverBorder: "hover:border-blue-400/50",
    hoverBg: "hover:bg-blue-500/20",
  },
};

interface ConnectionState {
  name: string;
  picture?: string | null;
}

interface ConnectionPillProps {
  accent: ConnectionAccent;
  user: ConnectionState | null | undefined;
  loading: boolean;
  loggingOut: boolean;
  loginHref: string;
  loginLabel: string;
  loginIcon?: React.ReactNode;
  disconnectTitle: string;
  onLogout: () => void;
  fullWidth?: boolean;
}

function ConnectionPill({
  accent,
  user,
  loading,
  loggingOut,
  loginHref,
  loginLabel,
  loginIcon,
  disconnectTitle,
  onLogout,
  fullWidth,
}: ConnectionPillProps) {
  if (loading) return null;
  const colors = ACCENT_CLASSES[accent];

  if (user) {
    return (
      <div
        className={`flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-2 py-1 sm:gap-2 sm:px-3 sm:py-1.5 ${fullWidth ? "w-full justify-between" : ""}`}
      >
        <div className="flex items-center gap-1.5 sm:gap-2">
          {user.picture ? (
            <Image src={user.picture} alt={user.name} width={20} height={20} className="rounded-full" />
          ) : (
            <User className={`h-4 w-4 ${colors.text}`} />
          )}
          <span className={`${fullWidth ? "" : "hidden sm:inline"} max-w-[8rem] truncate text-sm text-slate-300`}>
            {user.name}
          </span>
        </div>
        <button
          onClick={onLogout}
          disabled={loggingOut}
          title={disconnectTitle}
          className="cursor-pointer rounded-full p-0.5 text-slate-500 transition-colors hover:text-red-400 disabled:cursor-not-allowed"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  return (
    <motion.a
      href={loginHref}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      className={`inline-flex items-center gap-1.5 rounded-full border ${colors.border} ${colors.bg} px-2.5 py-1 text-xs font-medium ${colors.text} transition-colors ${colors.hoverBorder} ${colors.hoverBg} sm:gap-2 sm:px-4 sm:py-1.5 sm:text-sm ${fullWidth ? "w-full justify-center" : ""}`}
    >
      {loginIcon}
      {loginLabel}
    </motion.a>
  );
}

export function NavBar() {
  const pathname = usePathname();
  const navContentRef = useRef<HTMLDivElement>(null);
  const { data: googleUser, isLoading: googleLoading } = useGoogleUser();
  const { mutate: googleLogout, isPending: googleLoggingOut } = useGoogleLogout();
  const { data: user, isLoading } = useAniListUser();
  const { mutate: logout, isPending: loggingOut } = useAniListLogout();
  const { data: malUser, isLoading: malLoading } = useMALUser();
  const { mutate: malLogout, isPending: malLoggingOut } = useMALLogout();
  const { data: digest } = useDigest();

  const anyConnected = Boolean(googleUser || user || malUser);
  const hasUnreadDigest = Boolean(digest?.available && !digest.viewed);

  const connections = (
    <>
      <ConnectionPill
        accent="emerald"
        user={googleUser}
        loading={googleLoading}
        loggingOut={googleLoggingOut}
        loginHref={`${BACKEND_URL}/auth/google/login`}
        loginLabel="Sign in"
        disconnectTitle="Sign out"
        onLogout={() => googleLogout()}
        fullWidth
      />
      <ConnectionPill
        accent="teal"
        user={user}
        loading={isLoading}
        loggingOut={loggingOut}
        loginHref={`${BACKEND_URL}/auth/anilist/login`}
        loginLabel="Connect AniList"
        loginIcon={
          <svg className="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6.361 2.943 0 21.056h4.942l1.077-3.133H11.4l1.08 3.133H17.5L11.139 2.943zM7.241 14.03l1.97-5.735 1.964 5.735zm9.994 4.855-.78-2.26c1.5-.55 2.45-1.77 2.45-3.25 0-2.1-1.67-3.38-4.39-3.38h-1v2.24h.73c1.32 0 2.12.56 2.12 1.54 0 .92-.7 1.51-1.85 1.57l.87 2.52z" />
          </svg>
        }
        disconnectTitle="Disconnect AniList"
        onLogout={() => logout()}
        fullWidth
      />
      <ConnectionPill
        accent="blue"
        user={malUser}
        loading={malLoading}
        loggingOut={malLoggingOut}
        loginHref={`${BACKEND_URL}/auth/mal/login`}
        loginLabel="Connect MAL"
        disconnectTitle="Disconnect MAL"
        onLogout={() => malLogout()}
        fullWidth
      />
    </>
  );

  return (
    <nav className="sticky top-0 z-50 border-b border-transparent bg-slate-950/80 backdrop-blur-md [border-image:linear-gradient(to_right,rgba(168,85,247,0.35),rgba(99,102,241,0.25),rgba(236,72,153,0.25))_1] shadow-[0_1px_20px_-4px_rgba(168,85,247,0.25)]">
      <div
        ref={navContentRef}
        className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-y-2 gap-x-3 px-3 py-2 sm:px-4 sm:py-3"
      >
        <Link href="/" className="flex items-center gap-2 font-bold text-white">
          <Sparkles className="h-5 w-5 text-purple-400" />
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            AniDiscover
          </span>
        </Link>

        <div className="order-3 flex w-full flex-wrap items-center justify-center gap-1 border-t border-white/5 pt-2 sm:order-none sm:w-auto sm:justify-start sm:border-t-0 sm:pt-0 sm:pl-2">
          {NAV_LINKS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`relative flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm transition-colors ${
                  active ? "bg-white/10 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {label}
                {href === "/digest" && hasUnreadDigest && (
                  <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-pink-500 ring-2 ring-slate-950" />
                )}
              </Link>
            );
          })}
        </div>

        {/* sm and up: inline pills */}
        <div className="hidden items-center gap-3 sm:flex">
          <ConnectionPill
            accent="emerald"
            user={googleUser}
            loading={googleLoading}
            loggingOut={googleLoggingOut}
            loginHref={`${BACKEND_URL}/auth/google/login`}
            loginLabel="Sign in"
            disconnectTitle="Sign out"
            onLogout={() => googleLogout()}
          />
          {!googleLoading && <div className="h-5 w-px bg-white/10" />}
          <ConnectionPill
            accent="teal"
            user={user}
            loading={isLoading}
            loggingOut={loggingOut}
            loginHref={`${BACKEND_URL}/auth/anilist/login`}
            loginLabel="Connect AniList"
            loginIcon={
              <svg className="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6.361 2.943 0 21.056h4.942l1.077-3.133H11.4l1.08 3.133H17.5L11.139 2.943zM7.241 14.03l1.97-5.735 1.964 5.735zm9.994 4.855-.78-2.26c1.5-.55 2.45-1.77 2.45-3.25 0-2.1-1.67-3.38-4.39-3.38h-1v2.24h.73c1.32 0 2.12.56 2.12 1.54 0 .92-.7 1.51-1.85 1.57l.87 2.52z" />
              </svg>
            }
            disconnectTitle="Disconnect AniList"
            onLogout={() => logout()}
          />
          {!isLoading && !malLoading && <div className="h-5 w-px bg-white/10" />}
          <ConnectionPill
            accent="blue"
            user={malUser}
            loading={malLoading}
            loggingOut={malLoggingOut}
            loginHref={`${BACKEND_URL}/auth/mal/login`}
            loginLabel="Connect MAL"
            disconnectTitle="Disconnect MAL"
            onLogout={() => malLogout()}
          />
        </div>

        {/* below sm: single account popover */}
        <Popover.Root>
          <Popover.Trigger
            className="relative flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-white/10 bg-white/5 text-slate-300 transition-colors hover:text-white sm:hidden"
            title="Account"
          >
            <User className="h-4 w-4" />
            {anyConnected && (
              <span className="absolute right-0 top-0 h-2 w-2 rounded-full bg-emerald-400 ring-2 ring-slate-950" />
            )}
          </Popover.Trigger>
          <Popover.Portal>
            <Popover.Positioner anchor={navContentRef} sideOffset={8} align="end">
              <Popover.Popup className="z-50 w-64 rounded-2xl border border-white/10 bg-slate-900/95 p-3 shadow-xl backdrop-blur-md">
                <div className="flex flex-col gap-2">{connections}</div>
              </Popover.Popup>
            </Popover.Positioner>
          </Popover.Portal>
        </Popover.Root>
      </div>
    </nav>
  );
}
