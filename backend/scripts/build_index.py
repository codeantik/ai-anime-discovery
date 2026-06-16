"""
Offline index build script.
Phase 1 will flesh this out — fetches anime from AniList, embeds via the
provider interface, writes FAISS index to /data/anime.faiss and upserts
metadata into MongoDB.

Usage:
    uv run python -m scripts.build_index
"""


def main() -> None:
    print("build_index: placeholder — implement in Phase 1")


if __name__ == "__main__":
    main()
