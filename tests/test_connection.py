"""LiteLLM connection tests.

Env vars (LITELLM_API_BASE, LITELLM_API_KEY, LITELLM_MODEL) come from .env via conftest.py.

- Offline: the `litellm_client` fixture is configured from those env vars (no network).
- Live: one real round-trip through make_client -> stirrup LiteLLMClient -> provider.
  Run with `pytest -m live tests/test_connection.py`.
"""

from __future__ import annotations

import os

import pytest
from stirrup.core.models import TextBlock, UserMessage


def test_make_client_forwards_base_and_key(litellm_client, litellm_model):
    assert litellm_client.model_slug == litellm_model
    assert litellm_client.max_tokens == 256
    assert litellm_client._api_key == (os.getenv("LITELLM_API_KEY") or None)
    assert litellm_client._kwargs.get("api_base") == (os.getenv("LITELLM_API_BASE") or None)


@pytest.mark.live
async def test_litellm_live_roundtrip(litellm_client, litellm_model):
    if not (os.getenv("LITELLM_API_KEY") or os.getenv("LITELLM_API_BASE")):
        pytest.skip("No LITELLM_API_KEY / LITELLM_API_BASE configured")

    reply = await litellm_client.generate([UserMessage(content="Reply with exactly the word: pong")], tools={})

    text = "".join(b.text for b in reply.blocks if isinstance(b, TextBlock))
    assert "pong" in text.lower(), f"unexpected reply from {litellm_model}: {text!r}"
    assert reply.token_usage.input > 0
    assert reply.token_usage.output > 0
