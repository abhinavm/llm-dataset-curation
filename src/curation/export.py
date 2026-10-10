"""Write cleaned, chunked documents to Parquet / HF datasets format.

TODO: once pipeline.py produces real (doc_id, chunk_text, token_count)
records at corpus scale, write them out partitioned by source shard so
downstream consumers (e.g. a training data loader) can stream them.
"""
from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def write_parquet(records: list[dict], out_path: Path) -> None:
    table = pa.Table.from_pylist(records)
    pq.write_table(table, out_path)
