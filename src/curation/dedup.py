"""Exact and near-duplicate removal for a document corpus."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Iterator

from datasketch import MinHash, MinHashLSH


def _normalize(text: str) -> str:
    return " ".join(text.split()).lower()


def content_hash(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()


def exact_dedup(docs: Iterable[tuple[str, str]]) -> Iterator[tuple[str, str]]:
    """Drop exact duplicates by normalized content hash.

    docs: iterable of (doc_id, text). Yields the first occurrence of each
    distinct hash, in input order.
    """
    seen: set[str] = set()
    for doc_id, text in docs:
        h = content_hash(text)
        if h in seen:
            continue
        seen.add(h)
        yield doc_id, text


def _minhash(text: str, num_perm: int = 128, shingle_size: int = 5) -> MinHash:
    mh = MinHash(num_perm=num_perm)
    tokens = _normalize(text).split()
    shingles = {
        " ".join(tokens[i : i + shingle_size])
        for i in range(max(len(tokens) - shingle_size + 1, 1))
    }
    for s in shingles:
        mh.update(s.encode("utf-8"))
    return mh


@dataclass
class NearDedupResult:
    kept_ids: list[str]
    dropped_ids: list[str]


def near_dedup(
    docs: Iterable[tuple[str, str]],
    threshold: float = 0.8,
    num_perm: int = 128,
) -> NearDedupResult:
    """MinHash LSH near-duplicate removal.

    Keeps the first-seen document in each near-duplicate cluster. Threshold
    is Jaccard similarity on shingles; 0.8 is the common starting point from
    the C4/Gopher-style pretraining-data literature.
    """
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    kept: list[str] = []
    dropped: list[str] = []

    for doc_id, text in docs:
        mh = _minhash(text, num_perm=num_perm)
        if lsh.query(mh):
            dropped.append(doc_id)
            continue
        lsh.insert(doc_id, mh)
        kept.append(doc_id)

    return NearDedupResult(kept_ids=kept, dropped_ids=dropped)
