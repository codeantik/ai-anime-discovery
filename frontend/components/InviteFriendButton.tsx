"use client";

import { Check, Loader2, Users } from "lucide-react";
import { useState } from "react";
import { useCreateDuoInvite } from "@/lib/hooks/useDuo";

export function InviteFriendButton() {
  const { mutate, isPending } = useCreateDuoInvite();
  const [copied, setCopied] = useState(false);

  const handleClick = () => {
    if (isPending) return;
    mutate(undefined, {
      onSuccess: async ({ token }) => {
        await navigator.clipboard.writeText(`${window.location.origin}/duo/${token}`);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      },
    });
  };

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
      className={`flex shrink-0 cursor-pointer items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition-all duration-200
        ${copied
          ? "border border-emerald-500/30 bg-emerald-500/15 text-emerald-400"
          : "border border-pink-500/20 bg-pink-500/10 text-pink-300 hover:border-pink-400/40 hover:bg-pink-500/20"
        } disabled:cursor-not-allowed`}
    >
      {isPending ? (
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
      ) : copied ? (
        <Check className="h-3.5 w-3.5" />
      ) : (
        <Users className="h-3.5 w-3.5" />
      )}
      {copied ? "Link copied!" : "Invite a friend"}
    </button>
  );
}
