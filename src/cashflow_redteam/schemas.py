"""Shared data models: chart of accounts, transactions, spreads, cash flow results."""

from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from cashflow_redteam import COA_PATH


class CashFlowActivity(StrEnum):
    OPERATING = "Operating"
    INVESTING = "Investing"
    FINANCING = "Financing"


class Account(BaseModel):
    number: int
    name: str
    category: str
    activity: CashFlowActivity
    keywords: str


def load_chart_of_accounts(path: Path = COA_PATH) -> dict[int, Account]:
    """Parse the markdown chart-of-accounts table into {account_number: Account}."""
    accounts: dict[int, Account] = {}
    for line in path.read_text().splitlines():
        m = re.match(r"^\|\s*(\d{4})\s*\|(.+)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        name, category, activity, keywords = cells[:4]
        accounts[int(m.group(1))] = Account(
            number=int(m.group(1)), name=name, category=category,
            activity=CashFlowActivity(activity), keywords=keywords,
        )
    return accounts


# ---------------------------------------------------------------------------
# Ground truth (written by the generator, never shown to the agent)
# ---------------------------------------------------------------------------

class Transaction(BaseModel):
    txn_id: str
    date: date
    description: str
    amount: float = Field(description="Signed: + inflow (credit), - outflow (debit)")
    balance: float
    account: int = Field(description="Ground-truth chart-of-accounts number")


class StatementGroundTruth(BaseModel):
    statement_id: str
    company: str
    period_start: date
    period_end: date
    opening_balance: float
    closing_balance: float
    transactions: list[Transaction]
    # Debt service assumed for the proposed facility, needed for DSCR (not derivable from the statement).
    proposed_annual_debt_service: float


# ---------------------------------------------------------------------------
# Agent output (what the agent submits via the finish tool)
# ---------------------------------------------------------------------------

class SpreadLine(BaseModel):
    txn_ref: str = Field(description="Statement date + description, or txn id if available")
    date: date
    description: str
    amount: float
    account: int


class CashFlowSummary(BaseModel):
    operating: float
    investing: float
    financing: float
    net_change: float
    by_account: dict[int, float]
    monthly_operating: dict[str, float] = Field(description="YYYY-MM -> operating cash flow")
    dscr: float | None = None


class SpreadReport(BaseModel):
    """Final structured output of the spreading agent."""

    statement_ids: list[str]
    lines: list[SpreadLine]
    cashflow: CashFlowSummary
    narrative: str = Field(description="Short credit memo commentary")
