"""Monkey-patch for Harbor's codex agent (harbor 0.22.0, upstream unfixed).

Upstream `Codex._build_effective_config` writes only `command`/`args`/`url`
per `[mcp_servers.*]` table and never an `env = { ... }` block. Codex CLI does
not inherit parent env into MCP child processes, so MCP servers that need
secrets (APIFY_TOKEN etc.) see an empty environment and fail silently at
startup.

Values resolve via `Agent._get_env` (agent extra_env, then host os.environ,
where the CLI's .env auto-load puts them) and land as literals in the rendered
config.toml uploaded to the sandbox - same end state as the pre-0.22 heredoc
expansion.

TODO: remove when fixed in harbor
"""

from typing import Any

from harbor.agents.installed.codex import Codex

# server name → env-var names to forward into the codex MCP child process.
# Keep in sync with apps/<app>/mcp/cell.yaml env. Add a row per new app that
# wraps a remote MCP behind auth.
MCP_SERVER_ENV: dict[str, list[str]] = {
    "apify": ["APIFY_TOKEN"],
    "github": ["GITHUB_TOKEN"],
}

_orig_build_effective_config = Codex._build_effective_config


def _build_effective_config(
    self: Codex, openai_base_url: str | None = None
) -> dict[str, Any]:
    config = _orig_build_effective_config(self, openai_base_url)
    mcp_servers = config.get("mcp_servers")
    if isinstance(mcp_servers, dict):
        for name, server in mcp_servers.items():
            if not isinstance(server, dict):
                continue
            env = {
                var: value
                for var in MCP_SERVER_ENV.get(name, [])
                if (value := self._get_env(var)) is not None
            }
            if env:
                server["env"] = env
    return config


Codex._build_effective_config = _build_effective_config
