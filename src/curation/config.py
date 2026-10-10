"""Load pipeline thresholds from config.yaml, falling back to built-in
defaults when no file is present or a key is omitted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from curation.filter import FilterConfig

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.yaml"


@dataclass
class PipelineConfig:
    filter: FilterConfig = field(default_factory=FilterConfig)
    near_dedup_threshold: float = 0.8
    minhash_num_perm: int = 128
    max_tokens_per_chunk: int = 2048
    language: str = "en"


def load_config(path: Path | None = None) -> PipelineConfig:
    path = path or DEFAULT_CONFIG_PATH
    if not path.exists():
        return PipelineConfig()

    raw = yaml.safe_load(path.read_text()) or {}

    filter_cfg = FilterConfig(**raw.get("filter", {}))
    dedup_raw = raw.get("dedup", {})
    tokenize_raw = raw.get("tokenize", {})
    ingest_raw = raw.get("ingest", {})

    defaults = PipelineConfig()
    return PipelineConfig(
        filter=filter_cfg,
        near_dedup_threshold=dedup_raw.get("near_dedup_threshold", defaults.near_dedup_threshold),
        minhash_num_perm=dedup_raw.get("minhash_num_perm", defaults.minhash_num_perm),
        max_tokens_per_chunk=tokenize_raw.get("max_tokens_per_chunk", defaults.max_tokens_per_chunk),
        language=ingest_raw.get("language", defaults.language),
    )
