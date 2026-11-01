"""Create poisoned copies of benign statements.

data/benign_stmts/<id>.md  ->  data/poisoned_stmts/<objective>/<strategy>/<id>.md
plus data/poisoned_stmts/<objective>/<strategy>/manifest.json recording, per part, the file,
character offset and relative position (0..1) -> lets us analyse ASR vs. position ("lost in the middle").

Ground truth is unchanged except that the poisoned transaction(s) get their real account label; the
attack must not change the true cash flow (otherwise accuracy deltas would be confounded).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from cashflow_redteam.attacks.payloads import Objective, Payload, Strategy


def inject(statement_md: dict[str, str], payload: Payload, *, positions: list[float] | None = None,
           seed: int = 0) -> tuple[dict[str, str], dict]:
    """Insert payload parts into statements.

    statement_md: {statement_id: markdown} in chronological order.
    positions: relative positions (0..1) per part; default spreads f1 early, f2 mid, cue late.
    'memo' slots: append to / replace an existing transaction description (keep table well-formed!).
    'note' slots: insert as a statement note line, as llamaparse would emit for a PDF text box.
    Returns (poisoned_statements, manifest). TODO.
    """
    raise NotImplementedError


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate poisoned statement datasets")
    ap.add_argument("--objective", choices=[o.value for o in Objective], action="append")
    ap.add_argument("--strategy", choices=[s.value for s in Strategy], action="append")
    ap.add_argument("--src", type=Path, default=Path("data/benign_stmts"))
    ap.add_argument("--dst", type=Path, default=Path("data/poisoned_stmts"))
    args = ap.parse_args()
    raise NotImplementedError(args)


if __name__ == "__main__":
    main()
