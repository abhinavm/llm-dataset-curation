# llm-dataset-curation

A distributed pipeline that takes a raw text corpus and prepares it for LLM pretraining/fine-tuning: parsing, exact + near-duplicate removal, quality filtering, chunking/tokenization, and export to Parquet / Hugging Face `datasets` format.

Built to demonstrate the actual work behind "training data," not a toy wrapper around an LLM API.

## Why this exists

Most portfolio projects in this space are RAG demos. This one is scoped around what a data/ML infra team actually spends time on before a model ever sees the data: dedup at scale, quality heuristics, and knowing what you threw away and why.

## Architecture

```
Project Gutenberg (via Gutendex API)
      │
      ▼
  [ingest]        download plain-text books -> data/raw/
      │
      ▼
   [parse]        strip Gutenberg license header/footer boilerplate
      │
      ▼
   [dedup]        exact hash dedup -> MinHash LSH near-dedup
      │
      ▼
   [filter]       Gopher/C4-style quality heuristics
      │
      ▼
  [tokenize]      chunk + tokenize (tiktoken)
      │
      ▼
   [export]       Parquet / HF datasets format
      │
      ▼
  [metrics]       per-stage drop counts, token counts, throughput
```

## Status

MVP complete and benchmarked end-to-end against a real 499-book corpus (see Metrics below). Honest state of each stage:

| Stage | Status |
|---|---|
| `ingest.py` | implemented — downloads via Gutendex API with retry/backoff, idempotent re-runs |
| `parse.py` | implemented — strips Gutenberg license header/footer |
| `dedup.py` | implemented — exact dedup + MinHash LSH, unit tested |
| `filter.py` | implemented — length/symbol-ratio/repetition heuristics, unit tested |
| `tokenize.py` | implemented — tiktoken chunking |
| `export.py` | implemented — Parquet export |
| `metrics.py` | implemented — stage-level counters |
| `config.py` / `config.yaml` | implemented — thresholds are config-driven, not hardcoded, unit tested |
| `pipeline.py` | wires stages together, benchmarked against 499 real books |
| Spark version of near-dedup (for corpus-scale throughput) | not started — **the real run below shows exactly why this matters** |
| Airflow orchestration | not started (stretch goal) |

## Corpus

Project Gutenberg, via the [Gutendex](https://gutendex.com) API (a community-run read API over the Gutenberg catalog — avoids scraping gutenberg.org directly). Clean text, unambiguous licensing, easy to reason about in an interview.

```bash
python scripts/download_corpus.py --max-books 500
```

Start with a few hundred books (~hundreds of MB) to validate the pipeline and get real metrics; scale up `--max-books` afterward for a corpus-scale throughput benchmark. 5–20GB (several thousand books) is the stretch target — the point is to demonstrate correct, efficient processing, not to replicate Common Crawl.

## Running

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                                      # unit tests for dedup/filter/parse/config logic
python scripts/download_corpus.py --max-books 500
PYTHONPATH=src python -m curation.pipeline  # runs against data/raw/, prints per-stage metrics + throughput
```

## Metrics (real run, 499-book corpus, single M-series laptop core, no parallelism)

| Metric | Value |
|---|---|
| Raw docs in | 499 (376.6 MB) |
| Exact duplicates removed | 0 |
| Near-duplicates removed (MinHash LSH) | 1 |
| Docs removed by quality filter | 9 (all legitimate multi-volume compilations exceeding the 700k-word ceiling — e.g. Gibbon's *Decline and Fall of the Roman Empire*, Shakespeare's complete works — not a parsing bug) |
| Final doc count | 489 |
| Final chunk count (2048 tokens/chunk) | 37,923 |
| Final token count | 77,188,596 |
| Wall time | 1575 seconds (~26 min) |
| Throughput | 0.32 docs/sec, 0.24 MB/sec |

**The throughput number is the most important finding in this table, and it's bad.** 0.24 MB/sec means this single-threaded Python pipeline would take roughly 23 days to process 500GB and wouldn't finish a 5–20GB run in reasonable time either. Profiling points at `near_dedup`: MinHash shingles every 5-word window of each document and hashes each shingle with 128 permutations, in pure Python, on documents that are full-length books (hundreds of thousands of words) rather than short web pages. That cost is exactly what motivates the Spark version of near-dedup listed as a stretch goal above — this isn't a hypothetical scaling concern, it's the measured bottleneck in this corpus.
