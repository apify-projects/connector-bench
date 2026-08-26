"""Monkey-patch for Harbor's codex agent: route through a custom
`openrouter` model provider so MCP tools survive the OpenRouter setup.

# Problem (MCP connectors only)

Codex CLI uses OpenAI's Responses API over WebSocket by default. With
`OPENAI_BASE_URL=https://openrouter.ai/api/v1` (the project default, see
`.env`), codex tries `wss://openrouter.ai/api/v1/responses` which 404s
because OpenRouter does not implement the Responses API at that path.
Codex retries 5 times, then falls back to a degraded mode. In that
fallback, MCP tool definitions are not re-registered with the model,
so the agent emits a single commentary message, `turn.completed` fires
with zero tool calls, and every criterion fails.

The failure was MCP-only:
- codex + cli connector: 1.000 (shell tools survive the fallback)
- codex + skill connector: 1.000 (no tools required at runtime)
- codex + mcp connector: 0.000 (MCP tools never reach the model)

Symptom signature in the trial logs:
- agent/codex.txt: 5x `wss://openrouter.ai/api/v1/responses 404 Not Found`
- rollout jsonl: `turn.completed` immediately after one `agent_message`
- verifier stdout: `tool_calls=0`

# Fix

Merge into the effective config.toml:

  model_provider = "openrouter"
  disable_response_storage = true

  [model_providers.openrouter]
  name = "OpenRouter"
  base_url = "https://openrouter.ai/api/v1"
  wire_api = "responses"

Since harbor 0.22.0 the config is built as a dict in
`Codex._build_effective_config` and rendered via `toml.dumps` (which always
emits top-level scalars before tables, so the old TOML scoping hazard is
gone). This patch chains on top of `codex_mcp_env.py`'s wrapper of the same
method; import order in `connector_evals/__init__.py` matters and is enforced
alphabetically (codex_mcp_env before codex_wire_api).

Codex CLI deprecated `wire_api = "chat"` and only accepts
`wire_api = "responses"` at config-load time (see codex issue 7782).
`disable_response_storage = true` is required when the provider does
not implement the stored-response storage path (any provider other
than OpenAI's own endpoint).

TODO: remove when upstream harbor adds model-provider configuration to
its codex agent.
"""

from typing import Any

from harbor.agents.installed.codex import Codex

_prev_build_effective_config = Codex._build_effective_config


def _build_effective_config(
    self: Codex, openai_base_url: str | None = None
) -> dict[str, Any]:
    config = _prev_build_effective_config(self, openai_base_url)
    base_url = openai_base_url or self._get_env("OPENAI_BASE_URL") or ""
    if "openrouter.ai" not in base_url:
        return config

    config["model_provider"] = "openrouter"
    config["disable_response_storage"] = True
    providers = config.setdefault("model_providers", {})
    if isinstance(providers, dict):
        providers["openrouter"] = {
            "name": "OpenRouter",
            "base_url": base_url,
            "wire_api": "responses",
        }
    return config


Codex._build_effective_config = _build_effective_config
