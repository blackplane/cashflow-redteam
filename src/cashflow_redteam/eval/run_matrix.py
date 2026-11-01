"""Run the experiment matrix from configs/experiment.yaml.

For each (model, condition, defense, objective, strategy, months, company, repeat):
  run_spread(...) -> score_cell(...) -> append one JSON line to runs/<run_id>/results.jsonl
Also dumps the full message history per cell to runs/<run_id>/traces/ for qualitative analysis.

Resumable: skip cells whose key already exists in results.jsonl.
Concurrency: bounded asyncio.Semaphore per provider (rate limits).
"""

from __future__ import annotations

import argparse
from pathlib import Path


def expand_matrix(cfg: dict) -> list[dict]:
    """Expand config into a flat list of cell specs.

    Benign conditions (baseline, defense) do not vary objective/strategy -> fewer cells.
    TODO.
    """
    raise NotImplementedError


async def run_all(cfg: dict, run_dir: Path, concurrency: int) -> None:
    raise NotImplementedError


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the cashflow-redteam experiment matrix")
    ap.add_argument("--config", type=Path, default=Path("configs/experiment.yaml"))
    ap.add_argument("--run-dir", type=Path, default=None)
    ap.add_argument("--models", nargs="*", help="subset of model keys, e.g. A B")
    ap.add_argument("--conditions", nargs="*")
    ap.add_argument("--limit", type=int, default=None, help="max cells (smoke test)")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()
    raise NotImplementedError(args)


if __name__ == "__main__":
    main()
