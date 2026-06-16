# Claude Code Prompt — AI Anime Discovery (Phased Build)

> How to use: paste the whole thing as your first message in Claude Code. Or split it — put everything under **Project Context** + **Operating Rules** into a `CLAUDE.md` at the repo root, then paste from **Phase Plan** down as your kickoff message. Attach the `ai-anime-discovery-spec.md` if you want it to have the full reference too.

---

You are building a lean, free-tier full-stack AI app called **Anime Discovery**. Work through it **phase by phase**. After each phase: run it, verify the acceptance criteria yourself, commit, give me a short summary, and **stop and wait for my go-ahead** before starting the next phase. Do not build multiple phases in one go.

## Project Context

The app learns a user's anime taste, recommends titles via semantic embeddings + LLM re-ranking (with a reason per pick), and lets the user export their picks (CSV/JSON) or push them to their MyAnimeList.

The core architectural idea — respect it everywhere: the anime catalog is **bounded and slow-changing**, so we **embed it once offline**, ship the index with the app, and do **brute-force cosine similarity at request time**. At runtime we only embed the short user query. This is what keeps the app free and simple.

## Operating Rules (non-negotiable)

- **Free tier only.** No paid services. No managed vector DB. No always-on server beyond serverless functions. If a provider needs a key, add it to `.env.example` with a comment on where to get it, and tell me — never hardcode secrets.
- **No vector DB.** Brute-force cosine over the in-memory index is the correct choice at this scale. Don't add pgvector/Pinecone/etc.
- **Make the LLM/embedding provider swappable** behind a thin interface, with **Gemini, Groq, and local Ollama** as the intended free options. Default to whichever I have a key for; fall back to Ollama.
- **TypeScript strict mode.** Next.js App Router. Keep dependencies minimal — justify any new one.
- Plan before coding (use a todo list). Handle errors. Don't leave TODOs in shipped code.
- When something is genuinely ambiguous, ask me a single sharp question rather than guessing on something costly to undo.
- Commit at the end of each phase with a clear message. Keep the working tree clean.

## Tech Stack (pinned)

Next.js (App Router) + TypeScript · Vercel-targeted · AniList GraphQL (primary) / Jikan (fallback) for catalog data, both free no-key · embeddings + LLM via free tier (Gemini/Groq) or Ollama · index as SQLite (Turso-compatible) or static JSON · LangGraph.js for the re-rank graph and the later conversational agent · MyAnimeList OAuth2 for read/write.

## Known Gotchas (respect these — they will save hours)

- **MAL OAuth uses PKCE with the `plain` method** — `code_challenge` must EQUAL `code_verifier` (no S256 hashing). Most OAuth libraries default to S256; override it.
- Only embed the **user query** at runtime; the catalog is pre-embedded. Never embed the catalog inside a request handler.
- AniList/Jikan rate-limit — do catalog fetching only in the offline build script, with caching, never at runtime.
- MAL tokens are sensitive — httpOnly cookies, handle refresh, never expose client-side.

---

## Phase Plan

### Phase 0 — Scaffold & setup
**Build:** Next.js App Router + TS strict app; eslint/prettier; `.env.example`; sensible folder structure (`/app`, `/lib`, `/scripts`, `/data`); a `CLAUDE.md` capturing the context + rules above; git init.
**Acceptance:** `npm run dev` serves a placeholder home page; lint and typecheck pass; `.env.example` exists; clean initial commit.

### Phase 1 — Offline embedding index
**Build:** a script (`npm run build:index`) that pulls a few thousand top anime from AniList GraphQL (synopsis, genres, tags, year, format, mean score, cover URL), builds an embedding string (`synopsis + genres + tags + themes`), embeds them via the swappable provider, and writes the index (SQLite or JSON) into `/data`. Include a tiny CLI sanity check that takes a text query and prints nearest neighbors.
**Acceptance:** running the script produces an index file with N anime + vectors; the sanity check returns sensible neighbors for a sample query (e.g. "calm slice-of-life with great art"); the script is re-runnable and cached so it doesn't refetch needlessly.

### Phase 2 — MVP recommendation flow (no auth, no DB)
**Build:** a preferences form (genres, mood, themes, era, length, "titles I loved"); an API route that loads the index, embeds the query, runs brute-force cosine for top-K (~50), applies hard filters, then an LLM **re-rank** step returning top-N (~12) as structured JSON with `recommended_because` per pick; a results UI of cards (cover, title, reason, score); CSV/JSON export (client-side).
**Acceptance:** end-to-end — submit the form, get explained recommendations, export them. No database. Runs entirely on free tier. Re-rank output is reliably valid JSON.

### Phase 3 — MyAnimeList OAuth + personalization
**Build:** MAL OAuth2 **PKCE-plain** login; read the user's scored/completed history; build a **taste-vector centroid** from their highly-rated titles and blend it into retrieval; a per-card "Add to MyAnimeList" action via `PATCH /v2/anime/{id}/my_list_status`. Store tokens in httpOnly cookies with refresh handling.
**Acceptance:** connect a real MAL account, see recommendations personalized by history, and successfully add a pick to the user's list. Already-watched titles are excluded from recs.

### Phase 4 — V2 polish
**Build:** (a) a LangGraph conversational preference agent as an alternative to the form; (b) an offline **precision@k eval** script — hold out some of a test profile's favorites, run the recommender on the rest, report whether the held-out favorites resurface; (c) a GitHub Action that refreshes the index on a schedule.
**Acceptance:** the chat agent produces a structured preference profile that feeds the same pipeline; `npm run eval` prints a precision@k number; the scheduled Action runs the index build successfully.

---

Start with **Phase 0**. Plan it, build it, verify the acceptance criteria, commit, summarize what you did and how I can check it, then stop and wait for me.