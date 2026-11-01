"""cashflow-redteam: long-context indirect prompt injection against a bank-statement spreading agent."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
COA_PATH = REPO_ROOT / "bank-stmt-cashflow-chart-of-accounts.md"
