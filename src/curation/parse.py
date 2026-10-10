"""Raw bytes -> plain text, dispatched by source format.

TODO: wire up trafilatura for HTML and pymupdf for PDF once the corpus is
chosen. Plain-text sources (e.g. Gutenberg .txt) need no extraction step,
so that path is implemented now; it's also what the pipeline/tests exercise.
"""
from __future__ import annotations


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
