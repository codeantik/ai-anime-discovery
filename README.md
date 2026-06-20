# Anime Discovery

A full-stack AI app that learns your anime taste and recommends titles via semantic embeddings + LLM re-ranking — with a one-line reason for every pick. Connect AniList to personalize results from your watch history, chat with a conversational recommendation agent, or export your picks as CSV/JSON.

Built entirely on free-tier infrastructure: no managed vector DB, no always-on paid server.

## How it works

The anime catalog is bounded and slow-changing, so it's embedded **once, offline**, and shipped as a FAISS index. At request time only the user's short query is embedded — never the catalog.

```
POST /api/recommend
  → load FAISS index (in-memory)
  → embed user query
  → FAISS top-K similarity search (~50)
  → fetch metadata + apply hard filters (MongoDB)
  → LLM re-rank to top-N (~12), each with a "recommended_because" reason
  → return structured JSON
```

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js (App Router) + TypeScript, TailwindCSS + shadcn/ui, Framer Motion, TanStack Query, Zustand |
| Backend | FastAPI + uv |
| Vector search | FAISS (`faiss-cpu`), index built offline from AniList GraphQL data |
| Database | MongoDB Atlas (free M0) via `motor` |
| LLM / embeddings | Swappable provider interface — OpenAI by default; Gemini/Groq/Ollama as drop-in alternates |
| Agent | LangGraph (re-rank graph + conversational preference agent), Tavily for live web search |
| Observability | LangSmith (auto-instrumented) |
| Auth | AniList OAuth2 (drives taste-vector personalization) + MAL OAuth2 (PKCE-plain, independent second connection for "Add to MAL list"), both tokens in httpOnly cookies |

See [`CLAUDE.md`](./CLAUDE.md) for full architecture notes and non-negotiable project rules.

## Repo structure

```
/
├── frontend/        # Next.js App Router — Vercel-targeted
├── backend/         # FastAPI + uv — Railway/Render-targeted
│   ├── app/
│   │   ├── core/        # AniList/MAL clients, FAISS index loader, config
│   │   ├── models/      # Pydantic schemas
│   │   ├── providers/   # swappable embedding/LLM providers
│   │   ├── routers/     # auth, chat, list, mal, recommend, health
│   │   └── services/    # recommend, taste-vector, chat agent
│   └── scripts/         # build_index, eval, sanity_check
├── data/             # FAISS index artifact (data/anime.faiss)
├── .github/workflows/ # scheduled precision@k eval (weekly)
└── .env.example      # all required keys, documented
```

## Getting started

### Prerequisites
- Node.js + npm
- Python 3.13 + [uv](https://docs.astral.sh/uv/)
- A free MongoDB Atlas M0 cluster
- API keys per `.env.example` (OpenAI, AniList OAuth app, Tavily, LangSmith — all free tier)

### Setup

```bash
cp .env.example .env   # fill in your keys
```

**Backend** (from `/backend`):
```bash
uv sync
uv run python -m scripts.build_index   # one-time: fetch + embed catalog, write FAISS + MongoDB
uv run uvicorn app.main:app --reload --port 8001   # → http://localhost:8001
```

**Frontend** (from `/frontend`):
```bash
npm install
npm run dev   # → http://localhost:3000
```

### Useful commands

```bash
# Frontend
npm run dev | build | lint | typecheck | format

# Backend
uv run uvicorn app.main:app --reload --port 8001   # dev server
uv run python -m scripts.build_index                # rebuild offline index (cached, safe to re-run)
uv run python -m scripts.sanity_check "calm slice-of-life with great art"  # quick nearest-neighbor check
uv run python -m scripts.eval --k 10 --sample 200    # precision@k retrieval quality eval
```

A scheduled GitHub Action (`.github/workflows/eval.yml`) runs the precision@k eval weekly.

## Status

All seven build phases are complete: offline embedding index, semantic recommendation MVP with export, AniList OAuth + taste-vector personalization, a LangGraph conversational agent with scheduled evaluation, an anime detail page (trailer/studios/characters), MAL OAuth2 wired as an independent second connection ("Add to MAL list"), and a search/filter bar + FAISS-based "more like this" on the detail page. See [`CLAUDE.md`](./CLAUDE.md) for the full phase table and the non-negotiable rule that all UI work must be checked at mobile widths.
