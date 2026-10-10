"""CLI entrypoint: runs ingest -> dedup -> filter -> tokenize -> export
against the local data/raw sample, printing a per-stage metrics report.

This is the local/small-scale path for development. The Spark version of
dedup (for corpus-scale near-dedup) is a stretch goal -- see README.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from curation import dedup, export, filter as quality_filter, ingest, metrics, parse, tokenize


def run(raw_dir: Path, out_path: Path) -> metrics.Report:
    report = metrics.Report()

    raw_docs = list(ingest.iter_local_raw(raw_dir))
    docs = [(doc_id, parse.parse_gutenberg(raw)) for doc_id, raw in raw_docs]
    report.record("ingest", input_count=len(docs), output_count=len(docs))

    deduped = list(dedup.exact_dedup(docs))
    report.record("exact_dedup", input_count=len(docs), output_count=len(deduped))

    near = dedup.near_dedup(deduped)
    kept_ids = set(near.kept_ids)
    near_deduped = [(doc_id, text) for doc_id, text in deduped if doc_id in kept_ids]
    report.record("near_dedup", input_count=len(deduped), output_count=len(near_deduped))

    filtered = []
    drop_reasons: dict[str, int] = {}
    for doc_id, text in near_deduped:
        result = quality_filter.passes_quality_filter(text)
        if result.passed:
            filtered.append((doc_id, text))
        else:
            drop_reasons[result.reason] = drop_reasons.get(result.reason, 0) + 1
    from collections import Counter

    report.record("quality_filter", input_count=len(near_deduped), output_count=len(filtered), drop_reasons=Counter(drop_reasons))

    records = []
    for doc_id, text in filtered:
        for i, chunk in enumerate(tokenize.chunk_text(text)):
            records.append({"doc_id": f"{doc_id}_{i}", "text": chunk, "token_count": tokenize.token_count(chunk)})
    report.record("tokenize", input_count=len(filtered), output_count=len(records))

    if records:
        export.write_parquet(records, out_path)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/output.parquet"))
    args = parser.parse_args()

    report = run(args.raw_dir, args.out)
    print(json.dumps(report.summary(), indent=2))


if __name__ == "__main__":
    main()
