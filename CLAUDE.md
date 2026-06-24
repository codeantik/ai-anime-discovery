# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Anime Discovery** — a full-stack AI app that learns a user's anime taste, recommends titles via semantic embeddings + LLM re-ranking (with a reason per pick), and lets the user export picks (CSV/JSON) or push them to MyAnimeList.

> The project originated from a phased build prompt (`prompt.md`, since removed — see git history) targeting Next.js API routes + SQLite + MAL OAuth. The build evolved to the FastAPI/MongoDB/FAISS/AniList architecture documented below; this file is the current source of truth.

## Repo Structure

```
/
├── frontend/        # Next.js App Router (deploy to Vercel)
├── backend/         # FastAPI + uv (deploy to Railway/Render)
├── data/            # Shared artifacts: FAISS index, gitkeep
├── .env.example     # All keys documented here
└── CLAUDE.md
```

## Tech Stack

**Frontend** (`/frontend`)
- Next.js 16 App Router + TypeScript strict mode — Vercel-targeted
- TailwindCSS v4 + **shadcn/ui** (dark purple/indigo palette, components in `frontend/components/ui`)
- **Framer Motion** — all animations and micro-interactions
- **TanStack Query** (`@tanstack/react-query`) — all server-state fetching; custom hooks in `frontend/lib/hooks/`
- **Zustand** — cross-component UI state; stores in `frontend/lib/stores/`

**Backend** (`/backend`)
- **FastAPI** + **uv** for dependency management
- **Swappable provider interface** (`backend/app/providers/base.py`) — OpenAI default (`text-embedding-3-small` / `gpt-4o-mini`); alternates: Gemini, Groq, Ollama
- **FAISS** (`faiss-cpu`) — vector similarity search; index at `data/anime.faiss`, loaded into memory at startup
- **MongoDB Atlas** (free M0, via `motor`) — all structured data: anime metadata, user data, preferences, MAL history
- **LangGraph** (Python) — re-rank graph and conversational preference agent
- **LangSmith** — auto-instrumented observability; set `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY`
- **Tavily** (`tavily-python`) — web search when the agent needs live data

**Auth:** Three independent OAuth2 connections, all tokens in httpOnly cookies, handled by FastAPI:
- **AniList** (`backend/app/routers/auth.py`) — drives the taste-vector centroid and owns watchlist/feedback/history (all keyed by AniList user id). The de facto "is this person's anime data usable" check (`get_current_user`/`get_optional_user` in `backend/app/core/auth.py`).
- **MAL** (`backend/app/routers/mal_auth.py`, PKCE-plain) — second, independent connection used only for "Add to MAL list" — see "MAL OAuth Status" below.
- **Google** (`backend/app/routers/google_auth.py`) — app sign-in *identity only*, decoupled from the above. Issues our own signed JWT (`backend/app/core/session.py`, `app_session` cookie) backed by a `users` Mongo collection (`backend/app/services/users.py`, keyed by Google `sub`). Checked via `get_current_app_user`/`get_optional_app_user` in `backend/app/core/auth.py`. Deliberately *not* wired into watchlist/feedback/recommend — a Google-only sign-in has no anime data until AniList is also connected (this is "Option A" from the Phase 12 follow-up: minimal, no migration of existing AniList-keyed collections).

## Commands

```bash
# Frontend — run from /frontend
npm run dev          # Next.js dev server → http://localhost:3000
npm run build        # Production build
npm run lint         # ESLint
npm run typecheck    # tsc --noEmit
npm run format       # Prettier

# Backend — run from /backend
uv run uvicorn app.main:app --reload --port 8001   # FastAPI dev server → http://localhost:8001
uv run python -m scripts.build_index  # Offline: fetch anime, embed, write FAISS + MongoDB
uv run python -m scripts.eval         # precision@k evaluation
```

## Core Architecture

The catalog is **bounded and slow-changing**: embed once offline, ship the index, do FAISS similarity search at request time. No managed vector DB needed.

- **`/backend/scripts/build_index.py`** — fetches top anime from AniList GraphQL (synopsis, genres, tags, year, format, score, cover URL), embeds via the provider interface, writes `data/anime.faiss` and upserts metadata into MongoDB. Cached — safe to re-run.
- **`/backend/app/providers/`** — swappable `EmbeddingProvider` / `LLMProvider` base classes; concrete adapters per provider. Selected via `LLM_PROVIDER` env var.
- **FastAPI request flow:** `POST /api/recommend` → load FAISS (in-memory) → embed user query only → `faiss.search()` top-K (~50) → fetch metadata + hard filters from MongoDB → LLM re-rank top-N (~12) with `recommended_because` → return structured JSON.
- **Next.js** is UI only; calls FastAPI via TanStack Query hooks. No AI logic in Next.js API routes.
- **LangSmith** auto-instruments all LangChain/LangGraph calls — no manual trace setup needed.

## UI / Design Direction

Target audience is **Gen Z** — dark, expressive, alive:
- **Dark mode first** — deep slate-950 background, never light default
- **shadcn/ui** themed to purple/indigo/pink accent palette (CSS vars in `frontend/app/globals.css`)
- **Framer Motion** for all motion — entrance animations, card reveals, staggered lists, hover springs
- **Glassmorphism** anime result cards — `backdrop-blur`, semi-transparent bg + border
- **Bold typography** — large headings, tight tracking, gradient text for key phrases
- **Mobile-first** responsive grid
- Custom-styled all inputs/buttons — `rounded-xl` or `rounded-full`, no default browser appearance

## Non-Negotiable Rules

- **Free tier only.** No paid services, no managed vector DB (no pgvector/Pinecone/etc.), no always-on server beyond serverless functions.
- **LLM/embedding provider must be swappable.** Never hard-couple to a single provider.
- **Never embed the catalog at runtime** — only the short user query is embedded inside a request handler.
- **AniList/Jikan rate limits** — catalog fetching only in the offline build script, with caching.
- **MAL tokens** — httpOnly cookies only, handle token refresh, never expose client-side.
- Add any API key to `.env.example` with a comment. Never hardcode secrets.
- **Ask the user before installing any new npm or pip package**, or integrating any new external tool.
- **All UI changes must be responsive on small/mobile screens.** When touching `frontend/`, check the result at common mobile widths (~320–768px) before considering the task done: no horizontal overflow, no cramped/overlapping controls, nav/action rows must wrap or collapse gracefully rather than spill off-screen.

## MAL OAuth Gotcha

MAL OAuth2 uses **PKCE with the `plain` method**: `code_challenge` must equal `code_verifier` (no S256). Most OAuth libraries default to S256 — override explicitly.

## Phases

| Phase | Goal |
|-------|------|
| 0 | ✅ Scaffold: `frontend/` (Next.js) + `backend/` (FastAPI + uv), folder structure, git init |
| 1 | ✅ Offline embedding index (`uv run python -m scripts.build_index`) + sanity-check CLI |
| 2 | ✅ MVP: preferences form → FAISS retrieval → LLM re-rank → cards UI → CSV/JSON export |
| 3 | ✅ AniList OAuth, taste-vector centroid from history, "Add to AniList" per card (MAL OAuth scaffolded but unwired — see below) |
| 4 | ✅ LangGraph conversational agent, precision@k eval script, scheduled GitHub Action (`.github/workflows/eval.yml`) |
| 5 | ✅ Anime detail page (`frontend/app/anime/[id]/page.tsx`) with AniList trailer, studios, and characters |
| 6 | ✅ MAL OAuth2 wired as a second connection: `backend/app/routers/mal_auth.py` (login/callback/logout/me, PKCE-plain) + `backend/app/routers/mal.py` (`/api/mal/add`), "Add to MAL" button per card alongside "Add to AniList" |
| 7 | ✅ Search/filter bar on the recommendations grid (`frontend/components/FilterBar.tsx`); "More like this" on the anime detail page via FAISS k-NN (`GET /api/anime/{id}/similar`, `backend/app/core/index.py::get_similar`); results-persistence fix (`frontend/lib/stores/results.ts`) so navigating to a detail page and back no longer resets the discover flow; mobile-responsive pass on `NavBar`, `AnimeCard`, and `FilterBar` |
| 8 | ✅ Frontend chat UI (`frontend/app/chat/page.tsx`) for the existing backend-only `/api/chat` LangGraph agent (Phase 4) — message bubbles, inline recommendation cards linking to anime detail pages, "Chat" link in `NavBar`; client manages history, backend stays stateless per request |
| 9 | ✅ Per-user recommendation history: `backend/app/core/db.py` (Motor/MongoDB Atlas singleton, first real Mongo usage in the backend), `backend/app/services/history.py` (`recommendation_history` collection keyed by AniList user id) — `/api/recommend` and `/api/chat` now exclude previously-shown anime for logged-in users (falls back to no exclusion if too few candidates remain). Also fixed a pre-existing bug where `/api/recommend`/`/api/chat` could return duplicate `anilist_id` entries (deduped both the FAISS candidate list and the LLM rerank output in `backend/app/services/recommend.py`). |
| 10 | ✅ Watchlist (save for later): `backend/app/services/watchlist.py` (`watchlist` collection) + `backend/app/routers/watchlist.py` (`/api/watchlist` GET/add/delete), "Save" button per card (`frontend/components/AddToWatchlistButton.tsx`), `frontend/app/watchlist/page.tsx` |
| 11 | ✅ Thumbs up/down feedback that refines the taste vector: `backend/app/services/feedback.py` (`feedback` collection, `{anilist_id: signal}` per user) + `backend/app/routers/feedback.py` (`/api/feedback` GET/POST). `backend/app/services/taste.py::get_taste_vector` now blends explicit feedback (weight 2.5) into the AniList-score-weighted centroid — likes pull it toward them, dislikes push it away — and works even with zero AniList history if feedback exists. `backend/app/services/recommend.py` hard-excludes disliked `anilist_id`s from candidates (same fallback-if-too-few rule as seen-history exclusion, but dislikes are never resurfaced even in the fallback). Frontend: `frontend/components/FeedbackButtons.tsx` (thumbs icons, toggle-to-clear) wired into `AnimeCard.tsx`. |
| 12 | ✅ Authentication & authorization hardening: `backend/app/core/auth.py` — reusable `get_current_user` (401 if missing) / `get_optional_user` (degrades to `None`) FastAPI dependencies returning a `CurrentUser(id, access_token)`, replacing the per-router duplicated `_require_user_id()` checks in `watchlist.py`, `feedback.py`, and `list.py`; `recommend.py` and `chat.py` switched to `get_optional_user` (same anonymous-friendly behavior as before, now centralized). `frontend/middleware.ts` adds server-side route protection for `/watchlist`, redirecting to `/` when the `al_access_token` cookie is absent — the existing client-side "Connect AniList" prompt in `watchlist/page.tsx` remains as a fallback for stale/expired sessions. No roles/admin tier added — single-user-type app, so "authorization" means consistent ownership checks (act only on your own AniList user id), not a permissions matrix. |
| 13 | ✅ Google sign-in as a third, independent identity provider (decoupled from AniList/MAL data links — "Option A"): `backend/app/core/google_client.py` (OAuth2 code exchange + userinfo), `backend/app/core/session.py` (signs/verifies our own `app_session` JWT, `PyJWT`, 30-day TTL), `backend/app/services/users.py` (new `users` Mongo collection keyed by Google `sub`), `backend/app/routers/google_auth.py` (`/auth/google/login` with CSRF `state` cookie, `/callback`, `/logout`, `/me`). New `get_current_app_user`/`get_optional_app_user` dependencies in `backend/app/core/auth.py`, deliberately not wired into watchlist/feedback/recommend — a Google-only sign-in has no anime data until AniList is separately connected. Frontend: `frontend/lib/hooks/useGoogleAuth.ts` + a third NavBar pill. Requires `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`/`GOOGLE_REDIRECT_URI`/`SESSION_SECRET` in `.env` (see `.env.example` for the Google Cloud Console setup steps) — without them `/auth/google/login` still redirects correctly but Google will reject the empty `client_id`. |
| 14 | ✅ Taste-vector caching (`backend/app/core/cache.py`, in-memory TTL store; `backend/app/services/taste.py::get_taste_vector` caches per user for 120s, invalidated on feedback changes) + a personalized recommendation nudge (`frontend/components/ConnectAniListBanner.tsx`, shown when `personalized === false`). |
| 15 | ✅ In-app personalized digest — a daily "New For You" batch of taste-vector-only recommendations, snapshotted in Mongo so the NavBar can cheaply show an unread badge without recomputing: `backend/app/services/digest.py` (`digest` collection, `DIGEST_REFRESH` = 24h, reuses `services/recommend.py::recommend()` with no query and `services/taste.py::get_taste_vector` only — returns `None`/stale-fallback when there's no taste signal yet), `backend/app/routers/digest.py` (`GET /api/digest`, `POST /api/digest/viewed`), `DigestResponse` model in `backend/app/models/recommend.py`. Frontend: `frontend/lib/hooks/useDigest.ts`, `frontend/app/digest/page.tsx`, a new "For You" NavBar link with an unread-dot badge (`frontend/components/NavBar.tsx`). In-app only — no email/external service, per the free-tier/no-new-tool rule. |
| 16 | ✅ Shareable links for a single anime card or a whole watchlist: `backend/app/services/shares.py` (`shares` collection — cards store a token-keyed snapshot of `{owner_id, anilist_id, recommended_because}`; watchlist shares upsert one token per owner so re-sharing returns the same link) + `backend/app/routers/shares.py` (`POST /api/share/card`, `POST /api/share/watchlist` — both `get_current_user`-gated; `GET /api/share/{token}` — public, no auth, 404s on an unknown/missing token), `SharedResponse` model in `backend/app/models/recommend.py`. Watchlist shares resolve live (not frozen) against `services/watchlist.py::get_watchlist_ids`, so the link always reflects the owner's current list. Frontend: `frontend/lib/hooks/useShare.ts`, `frontend/components/ShareButton.tsx` (per-card, wired into `AnimeCard.tsx`, copies link to clipboard) + `frontend/components/ShareWatchlistButton.tsx` (wired into `watchlist/page.tsx` header), `frontend/components/ConnectToDiscoverBanner.tsx` (sign-in nudge for visitors), public `frontend/app/share/[token]/page.tsx` — deliberately outside `middleware.ts`'s auth gate; existing per-card action buttons (`FeedbackButtons`, `AddToAniListButton`, `AddToMALButton`, `AddToWatchlistButton`, `ShareButton`) already self-hide with no AniList session, so no extra guarding was needed for the anonymous case. |

All sixteen phases are complete. Build one phase at a time on future work — verify acceptance criteria, commit, summarize, wait for go-ahead.

## Phases 17–22 (planned, ordered by implementation complexity)

Phases 17–21 are complete; Phase 22 is queued and not yet built. Each reuses existing infrastructure (taste vector, FAISS index, shares, watchlist, digest) rather than new packages/services, per the Non-Negotiable Rules above. Because both the taste vector and FAISS-stored vectors are unit-normalized, cosine similarity between them is a plain dot product — the shared primitive for Phases 17, 18, and 21 (`backend/app/core/index.py::get_vector(anilist_id)` reconstructs a catalog anime's stored vector; dot it with `services/taste.py::get_taste_vector`).

| Phase | Goal |
|-------|------|
| 17 | ✅ "Taste Match" badge on the anime detail page: `index.py::get_vector(anilist_id)` (new helper using `index.reconstruct`, mirroring `get_similar`'s existing use of `reconstruct`) dotted with `get_taste_vector`, surfaced as `AnimeDetail.taste_match: float \| None` from `GET /api/anime/{anilist_id}` (switched to `get_optional_user`), rendered as a badge in `frontend/app/anime/[id]/page.tsx`. |
| 18 | ✅ Taste-based watchlist sorting: `GET /api/watchlist?sort=added\|taste` — when `taste`, sorts the existing `AnimeRecommendation[]` by `get_vector(anilist_id)` · taste vector (falls back to insertion order with no signal); sort toggle in `frontend/app/watchlist/page.tsx`. |
| 19 | ✅ "Share my digest" link: `services/shares.py::create_digest_share` (mirrors `create_watchlist_share`'s upsert-one-token-per-owner) + `POST /api/share/digest`; `GET /api/share/{token}` type-dispatch gains `"digest"`, live-resolved via `get_digest()` like watchlist shares; "Share my digest" button (`frontend/components/ShareDigestButton.tsx`) on `frontend/app/digest/page.tsx`. |
| 20 | ✅ Taste profile / genre insights page: `services/profile.py::get_taste_profile` aggregates genres/tags from the same AniList-history + feedback sources as the taste-vector centroid, weighted the same way, returning top-N normalized weights (cached/invalidated alongside the taste vector since it also fetches AniList history); `GET /api/taste/profile`, `frontend/app/taste/page.tsx` rendering plain CSS/Framer Motion bars (no charting library) + "Taste" NavBar link. |
| 21 | ✅ Seasonal / new-release radar: live AniList query (IDs + season/seasonYear/status only — catalog has neither today) cached 6h via `core/cache.py`, intersected with catalog `anilist_id`s via `index.py::get_faiss_idx_by_anilist_id`, ranked by taste-vector dot product (`index.py::get_vector`) for logged-in users or by `mean_score` otherwise; `services/seasonal.py`, `GET /api/seasonal` (`routers/seasonal.py`, `get_optional_user`), `SeasonalResponse` model, `frontend/app/seasonal/page.tsx` + `useSeasonal.ts` hook + "Seasonal" NavBar link. |
| 22 | Friend/group combined recommendations: new `services/duo.py` — `create_duo_invite` snapshots the owner's taste vector into a new `duo_invites` collection; the guest's live taste vector is averaged with it and re-normalized, then passed into the existing `recommend()` (taste-vector-only, same pattern as `digest.py`); `POST /api/duo/invite`, `GET /api/duo/{token}`, `frontend/app/duo/[token]/page.tsx`. |

Delivery process: ship one phase at a time, verify (including the mobile-width check for any UI), commit, summarize, and wait for explicit go-ahead before starting the next — do not start a phase before the previous one is approved.

## MAL OAuth Status

Phase 3 originally targeted MAL OAuth2; it was swapped for **AniList OAuth** because the MAL developer page lacks social login. Phase 6 wired up the leftover MAL client/router (`backend/app/core/mal_client.py`, `backend/app/routers/mal_auth.py`, `backend/app/routers/mal.py`) as an independent second connection — login + "Add to MAL list" only. It does **not** feed the taste-vector centroid; AniList remains the sole history source for recommendations. The PKCE-plain gotcha below applies to `mal_auth.py`'s `/login` endpoint.
