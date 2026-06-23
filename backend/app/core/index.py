"""FAISS index + metadata singleton — loaded once at startup."""

import json
from pathlib import Path

import faiss
import numpy as np

from app.core.config import DATA_DIR

_index: faiss.Index | None = None
_meta: dict[str, dict] | None = None
_anilist_to_faiss: dict[int, int] | None = None


def load_index() -> tuple[faiss.Index, dict[str, dict]]:
    global _index, _meta, _anilist_to_faiss
    if _index is not None and _meta is not None:
        return _index, _meta

    faiss_path = DATA_DIR / "anime.faiss"
    meta_path = DATA_DIR / "anime_meta.json"

    if not faiss_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {faiss_path}. "
            "Run: cd backend && uv run python -m scripts.build_index"
        )

    _index = faiss.read_index(str(faiss_path))
    _meta = json.loads(meta_path.read_text(encoding="utf-8"))
    _anilist_to_faiss = {v["anilist_id"]: int(k) for k, v in _meta.items() if "anilist_id" in v}
    return _index, _meta


def search(query_vec: np.ndarray, top_k: int = 80) -> list[tuple[int, float]]:
    index, _ = load_index()
    vec = query_vec.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
    scores, indices = index.search(vec, top_k)
    return [(int(idx), float(score)) for idx, score in zip(indices[0], scores[0]) if idx != -1]


def get_similar(faiss_idx: int, top_k: int = 8) -> list[tuple[int, float]]:
    index, _ = load_index()
    vec = index.reconstruct(faiss_idx).reshape(1, -1)
    scores, indices = index.search(vec, top_k + 1)
    return [
        (int(idx), float(score))
        for idx, score in zip(indices[0], scores[0])
        if idx != -1 and idx != faiss_idx
    ][:top_k]


def get_anime(faiss_idx: int) -> dict | None:
    _, meta = load_index()
    return meta.get(str(faiss_idx))


def get_faiss_idx_by_anilist_id(anilist_id: int) -> int | None:
    load_index()  # ensure _anilist_to_faiss is populated
    return _anilist_to_faiss.get(anilist_id) if _anilist_to_faiss else None


def get_vector(anilist_id: int) -> np.ndarray | None:
    """Reconstructs a catalog anime's stored (unit-normalized) embedding by anilist_id."""
    faiss_idx = get_faiss_idx_by_anilist_id(anilist_id)
    if faiss_idx is None:
        return None
    index, _ = load_index()
    return index.reconstruct(faiss_idx)
