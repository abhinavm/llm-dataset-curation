"""Pull the raw corpus into local/S3 storage.

TODO once the corpus source is finalized (see README "Corpus" section):
- Project Gutenberg: bulk mirror listing -> download a bounded subset of
  plain-text books.
- Wikipedia: download one language dump slice, decompress.

Should yield (doc_id, raw_bytes, source_path) tuples so `parse.py` can
handle format-specific extraction without knowing where the bytes came from.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator


def iter_local_raw(raw_dir: Path) -> Iterator[tuple[str, bytes]]:
    """Read already-downloaded raw files from disk. Placeholder until a
    real downloader is written -- lets the rest of the pipeline be built
    and tested against a hand-placed sample before the corpus is chosen.
    """
    for path in sorted(raw_dir.glob("*")):
        if path.is_file() and path.name != ".gitkeep":
            yield path.stem, path.read_bytes()
