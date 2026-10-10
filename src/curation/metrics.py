"""Per-stage counters for the pipeline's "what did we throw away and why" report."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class StageMetrics:
    stage: str
    input_count: int = 0
    output_count: int = 0
    drop_reasons: Counter = field(default_factory=Counter)

    @property
    def dropped(self) -> int:
        return self.input_count - self.output_count

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "dropped": self.dropped,
            "drop_reasons": dict(self.drop_reasons),
        }


class Report:
    def __init__(self) -> None:
        self.stages: list[StageMetrics] = []

    def record(self, stage: str, input_count: int, output_count: int, drop_reasons: Counter | None = None) -> None:
        self.stages.append(
            StageMetrics(stage=stage, input_count=input_count, output_count=output_count, drop_reasons=drop_reasons or Counter())
        )

    def summary(self) -> list[dict]:
        return [s.to_dict() for s in self.stages]
