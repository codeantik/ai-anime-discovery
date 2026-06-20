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

**Auth:** AniList OAuth2 (`backend/app/routers/auth.py`) and MAL OAuth2 (`backend/app/routers/mal_auth.py`, PKCE-plain), both tokens in httpOnly cookies, handled by FastAPI. AniList drives the taste-vector centroid; MAL is a second, independent connection used only for "Add to MAL list" — see "MAL OAuth Status" below.

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

All nine phases are complete. Build one phase at a time on future work — verify acceptance criteria, commit, summarize, wait for go-ahead.

## MAL OAuth Status

Phase 3 originally targeted MAL OAuth2; it was swapped for **AniList OAuth** because the MAL developer page lacks social login. Phase 6 wired up the leftover MAL client/router (`backend/app/core/mal_client.py`, `backend/app/routers/mal_auth.py`, `backend/app/routers/mal.py`) as an independent second connection — login + "Add to MAL list" only. It does **not** feed the taste-vector centroid; AniList remains the sole history source for recommendations. The PKCE-plain gotcha below applies to `mal_auth.py`'s `/login` endpoint.
