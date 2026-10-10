"""Quality heuristics, loosely following the C4 / Gopher pretraining-data rules.

Each rule is a cheap, explainable check -- no model inference -- so the
pipeline can run at corpus scale without a GPU. Perplexity-based filtering
is a documented stretch goal, not implemented here.
"""
from __future__ import annotations

from dataclasses import dataclass

SYMBOL_CHARS = set("#{}[]<>|\\^~`")


@dataclass
class FilterConfig:
    min_words: int = 50
    # Tuned for whole-book documents, not scraped web pages: this is a
    # safety ceiling against corrupted/concatenated files, not a quality
    # signal. War and Peace runs ~590k words and is a legitimate document;
    # a 100k ceiling (reasonable for a web page) rejected real novels
    # (Pride and Prejudice, the Sherlock Holmes collection, Moby Dick) the
    # first time this ran against actual Gutenberg books.
    max_words: int = 700_000
    max_symbol_ratio: float = 0.1
    max_top_line_repeat_ratio: float = 0.3
    min_mean_word_length: float = 2.0
    max_mean_word_length: float = 10.0


@dataclass
class FilterResult:
    passed: bool
    reason: str | None = None


def check_length(text: str, cfg: FilterConfig) -> FilterResult:
    n = len(text.split())
    if n < cfg.min_words:
        return FilterResult(False, f"too_short:{n}_words")
    if n > cfg.max_words:
        return FilterResult(False, f"too_long:{n}_words")
    return FilterResult(True)


def check_symbol_ratio(text: str, cfg: FilterConfig) -> FilterResult:
    if not text:
        return FilterResult(False, "empty")
    symbol_count = sum(1 for c in text if c in SYMBOL_CHARS)
    ratio = symbol_count / len(text)
    if ratio > cfg.max_symbol_ratio:
        return FilterResult(False, f"high_symbol_ratio:{ratio:.2f}")
    return FilterResult(True)


def check_line_repetition(text: str, cfg: FilterConfig) -> FilterResult:
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return FilterResult(False, "no_lines")
    if len(lines) == 1:
        return FilterResult(True)
    most_common_count = max(lines.count(l) for l in set(lines))
    ratio = most_common_count / len(lines)
    if ratio > cfg.max_top_line_repeat_ratio:
        return FilterResult(False, f"repetitive_lines:{ratio:.2f}")
    return FilterResult(True)


def check_mean_word_length(text: str, cfg: FilterConfig) -> FilterResult:
    words = text.split()
    if not words:
        return FilterResult(False, "no_words")
    mean_len = sum(len(w) for w in words) / len(words)
    if mean_len < cfg.min_mean_word_length or mean_len > cfg.max_mean_word_length:
        return FilterResult(False, f"mean_word_length:{mean_len:.2f}")
    return FilterResult(True)


RULES = [check_length, check_symbol_ratio, check_line_repetition, check_mean_word_length]


def passes_quality_filter(text: str, cfg: FilterConfig | None = None) -> FilterResult:
    """Run all rules; return the first failure, or passed=True if all pass."""
    cfg = cfg or FilterConfig()
    for rule in RULES:
        result = rule(text, cfg)
        if not result.passed:
            return result
    return FilterResult(True)
