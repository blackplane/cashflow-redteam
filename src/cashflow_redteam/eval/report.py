"""Aggregate results.jsonl into the results tables.

Primary table (one per defense), cells = mean +/- std over repeats & companies:

                     A          B          C
  Baseline        acc / OCF err / tokens / time
  Attack          acc / ASR / utility-under-attack
  Defense         acc / delta-acc vs baseline / overhead (tokens %, time %) / FPR
  Attack+Defense  acc / ASR / ASR reduction vs Attack

Secondary plots:
  - ASR vs. statement length (months) per strategy   (reproduces the paper's filler-length curve)
  - ASR vs. payload relative position                (lost-in-the-middle)
  - explicit vs. fragmented vs. distributed           (paper's main comparison)
  - defense overhead: tokens & latency vs. ASR reduction (Pareto)
"""

from __future__ import annotations

import argparse
from pathlib import Path


def load_results(run_dir: Path) -> list[dict]:
    raise NotImplementedError


def summary_table(rows: list[dict], defense: str) -> str:
    """Return markdown table in the layout above. TODO."""
    raise NotImplementedError


def main() -> None:
    ap = argparse.ArgumentParser(description="Summarise an experiment run")
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    raise NotImplementedError(args)


if __name__ == "__main__":
    main()
