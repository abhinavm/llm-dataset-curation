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

MVP functionally complete end-to-end, verified against real downloaded books (Alice in Wonderland, Pride and Prejudice, Sherlock Holmes, Moby Dick, Frankenstein). Honest state of each stage:

| Stage | Status |
|---|---|
| `ingest.py` | implemented — downloads via Gutendex API, idempotent re-runs |
| `parse.py` | implemented — strips Gutenberg license header/footer |
| `dedup.py` | implemented — exact dedup + MinHash LSH, unit tested |
| `filter.py` | implemented — length/symbol-ratio/repetition heuristics, unit tested |
| `tokenize.py` | implemented — tiktoken chunking |
| `export.py` | implemented — Parquet export |
| `metrics.py` | implemented — stage-level counters |
| `pipeline.py` | wires stages together, verified on real Gutenberg books |
| Spark version of near-dedup (for corpus-scale throughput) | not started (stretch goal) |
| Airflow orchestration | not started (stretch goal) |
| Full-corpus run + real metrics table below | not started — next step |

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
pytest                                      # unit tests for dedup/filter/parse logic
python scripts/download_corpus.py --max-books 500
PYTHONPATH=src python -m curation.pipeline  # runs against data/raw/, prints per-stage metrics
```

## Metrics (filled in once the full pipeline runs on the real corpus)

| Metric | Value |
|---|---|
| Raw docs in | — |
| Exact duplicates removed | — |
| Near-duplicates removed (MinHash LSH) | — |
| Docs removed by quality filter | — |
| Final doc count | — |
| Final token count | — |
| Throughput (docs/sec) | — |
