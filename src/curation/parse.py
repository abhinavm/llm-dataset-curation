"""Raw bytes -> plain text, dispatched by source format.

TODO: wire up trafilatura for HTML and pymupdf for PDF if a second source
is ever added. Gutenberg plain-text is the corpus for this project (see
README), so parse_gutenberg is the path pipeline.py actually uses.
"""
from __future__ import annotations

import re

# Every Gutenberg text file wraps the book in a license header and a
# footer with the same two marker lines, just with the edition-specific
# title substituted in. Stripping these out before dedup/filtering matters:
# left in, every book in the corpus shares a few hundred near-identical
# words of boilerplate, which would otherwise get flagged as a corpus-wide
# near-duplicate cluster instead of being treated as what it is -- metadata,
# not content.
_START_RE = re.compile(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.IGNORECASE | re.DOTALL)
_END_RE = re.compile(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG EBOOK.*", re.IGNORECASE | re.DOTALL)


def strip_gutenberg_boilerplate(text: str) -> str:
    start_match = _START_RE.search(text)
    body = text[start_match.end():] if start_match else text

    end_match = _END_RE.search(body)
    body = body[: end_match.start()] if end_match else body

    return body.strip()


def parse_gutenberg(raw: bytes, encoding: str = "utf-8") -> str:
    text = raw.decode(encoding, errors="replace")
    return strip_gutenberg_boilerplate(text)


def parse_plain_text(raw: bytes, encoding: str = "utf-8") -> str:
    return raw.decode(encoding, errors="replace")


def parse_html(raw: bytes) -> str:
    import trafilatura

    extracted = trafilatura.extract(raw.decode("utf-8", errors="replace"))
    return extracted or ""


def parse_pdf(raw: bytes) -> str:
    import fitz  # pymupdf

    doc = fitz.open(stream=raw, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)
