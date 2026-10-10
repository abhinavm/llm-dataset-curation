#!/usr/bin/env python
"""Download a bounded Project Gutenberg subset into data/raw/.

Usage:
    python scripts/download_corpus.py --max-books 500
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from curation import ingest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-books", type=int, default=500, help="number of books to download")
    parser.add_argument("--language", default="en")
    parser.add_argument("--raw-dir", type=Path, default=Path(__file__).resolve().parent.parent / "data" / "raw")
    args = parser.parse_args()

    saved = ingest.download_corpus(args.raw_dir, args.max_books, args.language)
    print(f"{len(saved)} books on disk in {args.raw_dir}")


if __name__ == "__main__":
    main()
