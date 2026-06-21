"""Minimal in-process TTL cache — no external dependency, single-process scope."""

import time

MISSING = object()

_store: dict[str, tuple[object, float]] = {}


def get(key: str, default=MISSING):
    """Returns `default` (MISSING sentinel by default) on a miss/expiry, so a cached
    None value can be distinguished from "not cached"."""
    entry = _store.get(key)
    if entry is None:
        return default
    value, expires_at = entry
    if time.monotonic() > expires_at:
        del _store[key]
        return default
    return value


def set(key: str, value, ttl: float) -> None:
    _store[key] = (value, time.monotonic() + ttl)


def invalidate(key: str) -> None:
    _store.pop(key, None)
