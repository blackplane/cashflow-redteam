"""Stirrup spreading agent: build + run one experiment cell."""

from __future__ import annotations

import os
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from stirrup import Agent
from stirrup.clients.litellm_client import LiteLLMClient

from cashflow_redteam.agent.prompts import SECURE_SYSTEM_PROMPT, TASK_PROMPT, VULNERABLE_SYSTEM_PROMPT
from cashflow_redteam.agent.tools import RunContext, build_tools

RM_EMAIL = "rm.credit@lender.example"


@dataclass
class ModelSpec:
    key: str                 # "A" | "B" | "C"
    litellm_id: str
    context_window: int
    max_tokens: int = 16_000


@dataclass
class RunResult:
    model: str
    condition: str
    defense: str
    statement_ids: list[str]
    ctx: RunContext
    finished: bool
    wall_time_s: float
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    turns: int = 0
    tool_calls: dict[str, int] = field(default_factory=dict)
    cost_usd: float | None = None
    error: str | None = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)


def make_client(spec: ModelSpec) -> LiteLLMClient:
    kwargs: dict[str, Any] = {}
    if base := os.getenv("LITELLM_API_BASE"):
        kwargs["api_base"] = base
    return LiteLLMClient(
        model=spec.litellm_id,
        max_tokens=spec.max_tokens,
        context_window_tokens=spec.context_window,
        api_key=os.getenv("LITELLM_API_KEY") or None,
        kwargs=kwargs or None,
    )


def build_agent(spec: ModelSpec, ctx: RunContext, *, max_turns: int = 40, code_exec: str = "none") -> Agent:
    tools, finish = build_tools(ctx)
    if code_exec == "local":
        from stirrup.tools import LocalCodeExecToolProvider
        tools.append(LocalCodeExecToolProvider())
    elif code_exec == "docker":
        from stirrup.tools.code_backends.docker import DockerCodeExecToolProvider
        tools.append(DockerCodeExecToolProvider("python:3.12-slim"))

    secure = ctx.defense in {"spotlight", "stacked"}
    system_prompt = (
        SECURE_SYSTEM_PROMPT.format(nonce=ctx.nonce, datamark=ctx.datamark) if secure else VULNERABLE_SYSTEM_PROMPT
    )
    return Agent(
        client=make_client(spec),
        name=f"spreader-{spec.key}",
        system_prompt=system_prompt,
        tools=tools,
        finish_tool=finish,
        max_turns=max_turns,
    )


async def run_spread(
    spec: ModelSpec,
    statement_dir: Path,
    statement_ids: list[str],
    *,
    company: str,
    proposed_annual_debt_service: float,
    condition: str,
    defense: str = "none",
    max_turns: int = 40,
    code_exec: str = "none",
    output_dir: Path | None = None,
) -> RunResult:
    ctx = RunContext(
        statement_dir=statement_dir,
        statement_ids=statement_ids,
        defense=defense,
        proposed_annual_debt_service=proposed_annual_debt_service,
        allowed_recipients={RM_EMAIL},
        nonce=secrets.token_hex(4),
    )

    agent = build_agent(spec, ctx, max_turns=max_turns, code_exec=code_exec)
    prompt = "[TASK]\n" + TASK_PROMPT.format(
        company=company, debt_service=proposed_annual_debt_service, rm_email=RM_EMAIL
    )

    t0 = time.perf_counter()
    result = RunResult(model=spec.key, condition=condition, defense=defense,
                       statement_ids=statement_ids, ctx=ctx, finished=False, wall_time_s=0.0)
    try:
        async with agent.session(output_dir=output_dir) as session:
            finish_params, history, metadata = await session.run(prompt)
        result.finished = finish_params is not None and ctx.report is not None
        result.raw_metadata = metadata
        _fill_usage(result, history, metadata)
    except Exception as e:  # noqa: BLE001 - record and continue the matrix
        result.error = f"{type(e).__name__}: {e}"
    result.wall_time_s = time.perf_counter() - t0
    return result


def _fill_usage(result: RunResult, history: list, metadata: dict[str, Any]) -> None:
    """Aggregate stirrup's per-message TokenUsage + tool counts into RunResult."""
    for u in metadata.get("token_usage", []):
        result.input_tokens += u.input
        result.output_tokens += u.answer
        result.reasoning_tokens += u.reasoning
    result.turns = len(metadata.get("token_usage", []))
    result.tool_calls = {k: len(v) for k, v in metadata.items() if not k.startswith("_") and k != "token_usage"}
    # TODO: cost via litellm.cost_per_token(model=..., prompt_tokens=..., completion_tokens=...)
