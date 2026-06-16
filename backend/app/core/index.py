"""FAISS index + metadata singleton — loaded once at startup."""

import json
from pathlib import Path

import faiss
import numpy as np

from app.core.config import DATA_DIR

_index: faiss.Index | None = None
_meta: dict[str, dict] | None = None


def load_index() -> tuple[faiss.Index, dict[str, dict]]:
    global _index, _meta
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
    return _index, _meta


def search(query_vec: np.ndarray, top_k: int = 80) -> list[tuple[int, float]]:
    index, _ = load_index()
    vec = query_vec.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
    scores, indices = index.search(vec, top_k)
    return [(int(idx), float(score)) for idx, score in zip(indices[0], scores[0]) if idx != -1]


def get_anime(faiss_idx: int) -> dict | None:
    _, meta = load_index()
    return meta.get(str(faiss_idx))
