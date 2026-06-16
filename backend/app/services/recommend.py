import json
import logging

import numpy as np

from app.core import index as idx_store
from app.models.recommend import AnimeRecommendation, RecommendRequest, RecommendResponse
from app.providers.factory import get_embedding_provider, get_llm_provider

logger = logging.getLogger(__name__)

TOP_K_SEARCH = 80
TOP_N_RERANK = 12

ERA_RANGES: dict[str, tuple[int | None, int | None]] = {
    "classic": (None, 1999),
    "2000s": (2000, 2009),
    "2010s": (2010, 2019),
    "recent": (2020, None),
}

LENGTH_RULES: dict[str, tuple[str | None, int | None, int | None]] = {
    # (format_match, min_episodes, max_episodes)
    "movie":  ("MOVIE", None, None),
    "short":  (None, None, 13),
    "season": (None, 13, 26),
    "long":   (None, 26, None),
}


def _build_query(prefs: RecommendRequest) -> str:
    parts: list[str] = []
    if prefs.genres:
        parts.append(f"genres: {', '.join(prefs.genres)}")
    if prefs.mood:
        parts.append(f"mood: {prefs.mood}")
    if prefs.themes:
        parts.append(f"themes: {', '.join(prefs.themes)}")
    if prefs.loved_titles:
        parts.append(f"similar to: {', '.join(prefs.loved_titles)}")
    if prefs.era and prefs.era != "any":
        parts.append(f"era: {prefs.era}")
    if prefs.length and prefs.length != "any":
        parts.append(f"length: {prefs.length}")
    return " | ".join(parts) if parts else "popular highly-rated anime"


def _passes_filters(anime: dict, prefs: RecommendRequest) -> bool:
    # Era filter
    if prefs.era and prefs.era != "any" and prefs.era in ERA_RANGES:
        lo, hi = ERA_RANGES[prefs.era]
        year = anime.get("year")
        if year:
            if lo and year < lo:
                return False
            if hi and year > hi:
                return False

    # Length filter
    if prefs.length and prefs.length != "any" and prefs.length in LENGTH_RULES:
        fmt_match, min_eps, max_eps = LENGTH_RULES[prefs.length]
        fmt = (anime.get("format") or "").upper()
        eps = anime.get("episodes") or 0

        if fmt_match:
            if fmt != fmt_match:
                return False
        else:
            if fmt == "MOVIE":
                return False
            if min_eps and eps < min_eps:
                return False
            if max_eps and eps > max_eps:
                return False

    return True


def _build_rerank_prompt(candidates: list[dict], prefs: RecommendRequest, top_n: int) -> str:
    prefs_lines = []
    if prefs.genres:
        prefs_lines.append(f"- Genres: {', '.join(prefs.genres)}")
    if prefs.mood:
        prefs_lines.append(f"- Mood: {prefs.mood}")
    if prefs.themes:
        prefs_lines.append(f"- Themes: {', '.join(prefs.themes)}")
    if prefs.era and prefs.era != "any":
        prefs_lines.append(f"- Era: {prefs.era}")
    if prefs.length and prefs.length != "any":
        prefs_lines.append(f"- Length: {prefs.length}")
    if prefs.loved_titles:
        prefs_lines.append(f"- Loved titles: {', '.join(prefs.loved_titles)}")
    prefs_text = "\n".join(prefs_lines) or "- Open to any great anime"

    slim_candidates = [
        {
            "anilist_id": c["anilist_id"],
            "title": c.get("title") or c.get("title_romaji"),
            "genres": c.get("genres", []),
            "synopsis": (c.get("synopsis") or "")[:200],
            "year": c.get("year"),
            "mean_score": c.get("mean_score"),
        }
        for c in candidates
    ]

    return f"""You are an expert anime recommender. Pick the best {top_n} anime from the candidates that match the user's preferences. Rank them best-first.

USER PREFERENCES:
{prefs_text}

CANDIDATES (JSON):
{json.dumps(slim_candidates, ensure_ascii=False)}

Return ONLY valid JSON — no markdown, no explanation outside the JSON:
{{
  "recommendations": [
    {{
      "anilist_id": <integer id from candidates>,
      "recommended_because": "<1-2 sentences: why this anime fits THIS user's specific taste>"
    }}
  ]
}}

Rules:
- Pick exactly {min(top_n, len(candidates))} anime
- Use only anilist_ids from the candidates list above
- recommended_because must be personalised to the user's stated preferences"""


async def recommend(
    prefs: RecommendRequest,
    taste_vec: np.ndarray | None = None,
) -> RecommendResponse:
    embedding_provider = get_embedding_provider()
    llm_provider = get_llm_provider()

    query = _build_query(prefs)

    # Embed query
    raw_vec = await embedding_provider.embed(query)
    query_np = np.array(raw_vec, dtype=np.float32)

    # Blend with personal taste vector when available (60/40 taste/query)
    if taste_vec is not None:
        blended = 0.6 * taste_vec + 0.4 * query_np
        norm = np.linalg.norm(blended)
        vec_np = (blended / norm) if norm > 0 else query_np
    else:
        vec_np = query_np

    # FAISS search
    results = idx_store.search(vec_np, top_k=TOP_K_SEARCH)

    # Fetch metadata + apply hard filters
    candidates: list[dict] = []
    for faiss_idx, score in results:
        anime = idx_store.get_anime(faiss_idx)
        if anime is None:
            continue
        if not _passes_filters(anime, prefs):
            continue
        candidates.append({**anime, "similarity": score})

    if not candidates:
        return RecommendResponse(
            recommendations=[], query_used=query, total_candidates=0
        )

    # LLM re-rank
    top_n = min(TOP_N_RERANK, len(candidates))
    prompt = _build_rerank_prompt(candidates[:50], prefs, top_n)

    try:
        raw = await llm_provider.complete_json(prompt)
        reranked = raw.get("recommendations", [])
    except Exception as e:
        logger.warning(f"LLM rerank failed ({e}), falling back to similarity order.")
        reranked = [{"anilist_id": c["anilist_id"], "recommended_because": "Highly similar to your taste."} for c in candidates[:top_n]]

    # Map anilist_id → full metadata
    anilist_to_candidate = {c["anilist_id"]: c for c in candidates}
    recommendations: list[AnimeRecommendation] = []
    for item in reranked:
        aid = item.get("anilist_id")
        anime = anilist_to_candidate.get(aid)
        if not anime:
            continue
        recommendations.append(
            AnimeRecommendation(
                anilist_id=aid,
                title=anime.get("title") or anime.get("title_romaji") or "Unknown",
                title_romaji=anime.get("title_romaji"),
                synopsis=anime.get("synopsis") or "",
                genres=anime.get("genres") or [],
                tags=anime.get("tags") or [],
                year=anime.get("year"),
                format=anime.get("format"),
                mean_score=anime.get("mean_score"),
                episodes=anime.get("episodes"),
                cover_image=anime.get("cover_image"),
                recommended_because=item.get("recommended_because", ""),
                similarity=anime["similarity"],
            )
        )

    return RecommendResponse(
        recommendations=recommendations,
        query_used=query,
        total_candidates=len(candidates),
    )
