"""CLI entrypoint: runs ingest -> dedup -> filter -> tokenize -> export
against the local data/raw sample, printing a per-stage metrics report
plus overall throughput.

This is the local/small-scale path for development. The Spark version of
dedup (for corpus-scale near-dedup) is a stretch goal -- see README.
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

from curation import dedup, export, filter as quality_filter, ingest, metrics, parse, tokenize
from curation.config import PipelineConfig, load_config


def run(raw_dir: Path, out_path: Path, config: PipelineConfig | None = None) -> tuple[metrics.Report, dict]:
    config = config or load_config()
    report = metrics.Report()
    start = time.perf_counter()

    raw_docs = list(ingest.iter_local_raw(raw_dir))
    raw_bytes = sum(len(raw) for _, raw in raw_docs)
    docs = [(doc_id, parse.parse_gutenberg(raw)) for doc_id, raw in raw_docs]
    report.record("ingest", input_count=len(docs), output_count=len(docs))

    deduped = list(dedup.exact_dedup(docs))
    report.record("exact_dedup", input_count=len(docs), output_count=len(deduped))

    near = dedup.near_dedup(deduped, threshold=config.near_dedup_threshold, num_perm=config.minhash_num_perm)
    kept_ids = set(near.kept_ids)
    near_deduped = [(doc_id, text) for doc_id, text in deduped if doc_id in kept_ids]
    report.record("near_dedup", input_count=len(deduped), output_count=len(near_deduped))

    filtered = []
    drop_reasons: dict[str, int] = {}
    for doc_id, text in near_deduped:
        result = quality_filter.passes_quality_filter(text, config.filter)
        if result.passed:
            filtered.append((doc_id, text))
        else:
            drop_reasons[result.reason] = drop_reasons.get(result.reason, 0) + 1

    report.record("quality_filter", input_count=len(near_deduped), output_count=len(filtered), drop_reasons=Counter(drop_reasons))

    records = []
    for doc_id, text in filtered:
        for i, chunk in enumerate(tokenize.chunk_text(text, max_tokens=config.max_tokens_per_chunk)):
            records.append({"doc_id": f"{doc_id}_{i}", "text": chunk, "token_count": tokenize.token_count(chunk)})
    report.record("tokenize", input_count=len(filtered), output_count=len(records))

    if records:
        export.write_parquet(records, out_path)

    elapsed = time.perf_counter() - start
    total_tokens = sum(r["token_count"] for r in records)
    throughput = {
        "raw_docs": len(raw_docs),
        "raw_mb": round(raw_bytes / 1_000_000, 2),
        "final_chunks": len(records),
        "final_tokens": total_tokens,
        "elapsed_seconds": round(elapsed, 2),
        "docs_per_second": round(len(raw_docs) / elapsed, 2) if elapsed > 0 else None,
        "mb_per_second": round((raw_bytes / 1_000_000) / elapsed, 2) if elapsed > 0 else None,
    }

    return report, throughput


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/output.parquet"))
    parser.add_argument("--config", type=Path, default=None, help="path to config.yaml (default: repo root config.yaml)")
    args = parser.parse_args()

    config = load_config(args.config)
    report, throughput = run(args.raw_dir, args.out, config)
    print(json.dumps({"stages": report.summary(), "throughput": throughput}, indent=2))


if __name__ == "__main__":
    main()
