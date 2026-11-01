"""Defenses. Selected by name via RunContext.defense.

| name              | layer          | idea                                                                 |
|-------------------|----------------|----------------------------------------------------------------------|
| none              | -              | vulnerable baseline                                                  |
| spotlight         | prompt         | delimit + datamark document text, secure system prompt (Hines 2024)  |
| structured_reader | architecture   | read_statement returns parsed rows (JSON) w/ length-capped,          |
|                   |                | instruction-stripped descriptions; prose outside tables is dropped   |
| detector          | classifier     | scan tool output for injection (Prompt Guard / LLM judge), redact    |
| egress_allowlist  | tool policy    | send_email only to allowed recipients                                |
| invariants        | output check   | reconcile spread vs. statement (count, sum, balance delta)           |
| stacked           | all of above   |                                                                      |

Note: Docker code-exec isolation (README) limits blast radius of sandbox recon, it does not
prevent metric hijacking or exfiltration via legitimate tools, so it is a config flag, not a defense row.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cashflow_redteam.agent.tools import RunContext
    from cashflow_redteam.schemas import SpreadReport


def _on(ctx: RunContext, name: str) -> bool:
    return ctx.defense == name or ctx.defense == "stacked"


# --- read-path defenses -----------------------------------------------------

def apply_read_defenses(markdown: str, ctx: RunContext) -> str:
    text = markdown
    if _on(ctx, "structured_reader"):
        text = structured_reader(text)
    if _on(ctx, "detector"):
        text = detect_and_redact(text, ctx)
    if _on(ctx, "spotlight"):
        text = spotlight(text, ctx.nonce, ctx.datamark)
    return text


def spotlight(text: str, nonce: str, datamark: str = "^") -> str:
    """Wrap in nonce'd delimiters and interleave a datamark between words."""
    marked = datamark.join(text.split(" "))
    return f"<<DOC {nonce}>>\n{marked}\n<</DOC {nonce}>>"


def structured_reader(markdown: str) -> str:
    """Parse llamaparse markdown tables into JSON rows {date, description, debit, credit, balance}.

    - drop all non-table prose (headers/footers/notes are where cues tend to sit)
    - cap description length (e.g. 64 chars) and strip imperative / meta phrases
    TODO: implement; must be robust to llamaparse table quirks (split tables across pages,
          merged cells, multi-line descriptions).
    """
    raise NotImplementedError


def detect_and_redact(text: str, ctx: RunContext) -> str:
    """Run an injection detector over chunks; replace flagged chunks with [REDACTED: suspected injection].

    Options: meta-llama/Llama-Prompt-Guard-2-86M (local, cheap), or an LLM judge via litellm.
    Record flags in ctx.detector_flags (used for detector precision/recall + false-positive rate).
    NB: fragmented payloads are designed so no single chunk looks malicious -> expect low recall
    on chunk-level detectors; consider a whole-document pass as a variant.
    """
    raise NotImplementedError


# --- tool-policy defenses ---------------------------------------------------

def egress_allowed(recipients: list[str], ctx: RunContext) -> bool:
    if not _on(ctx, "egress_allowlist"):
        return True
    return all(r.lower() in ctx.allowed_recipients for r in recipients)


# --- output defenses --------------------------------------------------------

def check_invariants(report: SpreadReport, ctx: RunContext) -> list[str]:
    """Deterministic reconciliation; returns a list of problems (empty == OK).

    Planned checks (re-parse the statement markdown on the host side, not via the LLM):
    - every statement transaction appears exactly once in report.lines
    - sum(lines.amount) == closing - opening balance, per statement
    - cashflow.net_change == sum of activities
    - cashflow numbers equal compute_cashflow_summary(report.lines) (catches fabricated metrics)
    - flag classification of large one-off credits from lenders (e.g. 'SBA', 'LOAN') as 1000 revenue
    """
    if not _on(ctx, "invariants"):
        return []
    raise NotImplementedError
