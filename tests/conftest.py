import os

import pytest
import yaml
from dotenv import load_dotenv

from cashflow_redteam.agent.app import ModelSpec, make_client

# tests/data/ (exposed by pytest-datadir as `shared_datadir`) holds symlinks to the repo's
# .env and configs/experiment.yaml; pytest-datadir copies the link targets into a tmp dir.


@pytest.fixture(autouse=True)
def _load_env(shared_datadir):
    load_dotenv(shared_datadir / ".env")


@pytest.fixture
def litellm_model(shared_datadir) -> str:
    """LITELLM_MODEL from .env, falling back to the claude model in experiment.yaml."""
    if model := os.getenv("LITELLM_MODEL"):
        return model
    cfg = yaml.safe_load((shared_datadir / "experiment.yaml").read_text())
    return cfg["models"]["claude"]["litellm_id"]


@pytest.fixture
def litellm_client(litellm_model):
    """A stirrup LiteLLMClient built through the app's make_client, configured from .env."""
    return make_client(ModelSpec(key="T", litellm_id=litellm_model, context_window=32_000, max_tokens=256))
