# llm-dataset-curation

A distributed pipeline that takes a raw text corpus and prepares it for LLM pretraining/fine-tuning: parsing, exact + near-duplicate removal, quality filtering, chunking/tokenization, and export to Parquet / Hugging Face `datasets` format.

Built to demonstrate the actual work behind "training data," not a toy wrapper around an LLM API.

## Why this exists

Most portfolio projects in this space are RAG demos. This one is scoped around what a data/ML infra team actually spends time on before a model ever sees the data: dedup at scale, quality heuristics, and knowing what you threw away and why.

## Architecture

```
raw corpus (S3/local)
      │
      ▼
   [parse]        HTML/PDF -> plain text (trafilatura, pymupdf)
      │
      ▼
   [dedup]        exact hash dedup -> MinHash LSH near-dedup (PySpark)
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

MVP in progress. Honest state of each stage:

| Stage | Status |
|---|---|
| `ingest.py` | stub — corpus not yet chosen, see below |
| `parse.py` | stub |
| `dedup.py` | implemented — exact dedup + MinHash LSH, unit tested |
| `filter.py` | implemented — length/symbol-ratio/repetition heuristics, unit tested |
| `tokenize.py` | stub |
| `export.py` | stub |
| `metrics.py` | implemented — stage-level counters |
| `pipeline.py` | wires stages together, runs on a local sample |
| Spark version of dedup | not started (stretch goal) |
| Airflow orchestration | not started (stretch goal) |

## Corpus

Not yet finalized. Candidates, in order of preference:
- Project Gutenberg subset (clean text, unambiguous licensing, easy to reason about in an interview)
- A single-language Wikipedia dump slice

Target size: 5–20GB raw, intentionally bounded — the point is to demonstrate correct and efficient processing, not to replicate Common Crawl.

## Running

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                      # unit tests for dedup/filter logic
python -m curation.pipeline --help
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
