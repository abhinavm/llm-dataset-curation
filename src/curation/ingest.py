"""Pull a bounded Project Gutenberg subset into local raw storage.

Uses the Gutendex API (gutendex.com) for catalog metadata -- it's a
community-run read API over the Gutenberg catalog, so this doesn't scrape
gutenberg.org directly. Each catalog entry's `formats` dict points at the
actual book file (hosted on Gutenberg's own mirrors); we download the
plain-text UTF-8 format when a book has one and skip it otherwise (some
older entries are scan-only / HTML-only).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Iterator

import requests

GUTENDEX_BASE = "https://gutendex.com/books"
_TEXT_FORMAT_KEYS = ("text/plain; charset=utf-8", "text/plain; charset=us-ascii", "text/plain")


def iter_local_raw(raw_dir: Path) -> Iterator[tuple[str, bytes]]:
    """Read already-downloaded raw files from disk."""
    for path in sorted(raw_dir.glob("*.txt")):
        yield path.stem, path.read_bytes()


def _iter_catalog(language: str, max_books: int) -> Iterator[dict]:
    """Page through Gutendex, yielding book metadata dicts until max_books
    with a usable plain-text format have been seen."""
    url = GUTENDEX_BASE
    params = {"languages": language}
    seen = 0
    while url and seen < max_books:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        for book in payload.get("results", []):
            if seen >= max_books:
                return
            yield book
            seen += 1
        url = payload.get("next")
        params = None  # `next` is already a full URL with params baked in
        time.sleep(0.5)  # be polite to a free, community-run API


def _text_url(book: dict) -> str | None:
    formats = book.get("formats", {})
    for key in _TEXT_FORMAT_KEYS:
        if key in formats:
            return formats[key]
    return None


def download_corpus(raw_dir: Path, max_books: int, language: str = "en") -> list[Path]:
    """Download up to max_books plain-text Gutenberg books into raw_dir.
    Idempotent: books already on disk are skipped, so re-running with a
    larger max_books only fetches the delta.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    for book in _iter_catalog(language, max_books):
        book_id = book["id"]
        dest = raw_dir / f"{book_id}.txt"
        if dest.exists():
            saved.append(dest)
            continue

        text_url = _text_url(book)
        if text_url is None:
            continue

        resp = requests.get(text_url, timeout=30)
        if resp.status_code != 200:
            continue

        dest.write_bytes(resp.content)
        saved.append(dest)
        time.sleep(0.5)

    return saved
