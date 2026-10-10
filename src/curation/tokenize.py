"""Chunk + tokenize cleaned documents ahead of export."""
from __future__ import annotations

from typing import Iterator

import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")


def token_count(text: str) -> int:
    return len(_ENCODING.encode(text))


def chunk_text(text: str, max_tokens: int = 2048) -> Iterator[str]:
    """Split text into chunks of at most max_tokens, on token boundaries."""
    tokens = _ENCODING.encode(text)
    for i in range(0, len(tokens), max_tokens):
        yield _ENCODING.decode(tokens[i : i + max_tokens])
