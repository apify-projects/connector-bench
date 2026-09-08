import json
import os
import re
from pathlib import Path

from rewardkit import criterion
from rewardkit.criteria._trajectory import collect_tool_calls, load_trajectory

TRAJECTORY_PATH = "/logs/agent/trajectory.json"

_connectors = json.loads(os.environ.get("CONNECTOR_EVALS_CONNECTORS_JSON") or "{}")
_default_connector = os.environ.get("CONNECTOR_EVALS_CONNECTOR") or None


def _resolve(app: str) -> str | None:
    ch = _connectors.get(app) or _default_connector
    return "cli" if ch in ("skill", "cli+skill") else ch


CONNECTORS = {"notion": _resolve("notion"), "linear": _resolve("linear")}


def _tool_calls() -> list[dict]:
    data = load_trajectory(TRAJECTORY_PATH)
    return collect_tool_calls(data) if data else []


# Connector matching mirrored from src/connector_evals/metrics.py (cannot import the
# package inside the verifier container); keep both in sync manually. Per-app MCP
# tool allowlists cover harnesses that strip the server prefix from tool names
# (codex); claude-code / opencode prefixes are caught by the prefix check.
APPS = {
    "notion": {
        "mcp_name_prefixes": ("notion_", "notion-", "mcp__notion__"),
        "mcp_tools": {
            "search", "fetch", "retrieve-a-page", "retrieve-page-markdown",
            "retrieve-a-block", "retrieve-block-children", "retrieve-a-database",
            "retrieve-a-data-source", "query-data-source", "retrieve-comments",
            "list-all-users", "retrieve-a-user", "retrieve-your-token-s-bot-user",
        },
        "cli_prefix": "ntn ",
        "api_hosts": ("api.notion.com",),
    },
    "linear": {
        "mcp_name_prefixes": ("linear_", "linear-", "mcp__linear__"),
        "mcp_tools": {
            "list-issues", "get-issue", "list-teams", "get-team", "list-projects",
            "get-project", "list-cycles", "list-comments", "list-issue-labels",
            "list-issue-statuses", "get-issue-status", "list-users", "get-user",
            "get-workspace", "list-documents", "get-document", "list-milestones",
            "get-milestone", "search-documentation",
        },
        "cli_prefix": "linear ",
        "api_hosts": ("api.linear.app",),
    },
}
SHELL_TOOLS = {"bash", "exec_command", "shell", "run_terminal_cmd", "local_shell"}
WEBFETCH_TOOLS = {"webfetch", "web_fetch"}
# HTTP-issuing markers gate the api match, same as metrics.py `_is_api_escape`.
HTTP_MARKERS = (
    "curl", "wget", "httpie", "xh ",
    "urlopen", "urlretrieve", "requests.", "httpx", "aiohttp", "fetch(",
)


def _normalize_mcp_tool(name: str, app: str) -> str:
    for prefix in APPS[app]["mcp_name_prefixes"]:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    return name.replace("_", "-")


def _matches(tc: dict, app: str, connector: str | None) -> bool:
    if not connector:
        return True
    spec = APPS[app]
    name = (tc.get("function_name") or "").lower()
    args = tc.get("arguments") or {}
    cmd = ((args.get("command") or args.get("cmd")) or "").lstrip()
    # Agents often prefix with `cd /app && ` (the mcp-cli instruction says to
    # run from /app); strip it so the connector prefix check still matches.
    cmd = re.sub(r"^(?:cd\s+\S+\s*&&\s*)+", "", cmd)
    if connector == "mcp":
        return name.startswith(spec["mcp_name_prefixes"]) or _normalize_mcp_tool(name, app) in spec["mcp_tools"]
    if connector == "cli":
        return name in SHELL_TOOLS and cmd.startswith(spec["cli_prefix"])
    if connector == "mcpc":
        return name in SHELL_TOOLS and cmd.startswith("mcpc ")
    if connector == "mcporter":
        return name in SHELL_TOOLS and cmd.startswith("mcporter ")
    if connector == "mcp-cli":
        return name in SHELL_TOOLS and cmd.startswith("mcp-cli ")
    if connector == "api":
        url = str(args.get("url") or "")
        if name in WEBFETCH_TOOLS:
            return any(h in url for h in spec["api_hosts"])
        return name in SHELL_TOOLS and any(h in cmd for h in spec["api_hosts"]) and any(
            m in cmd for m in HTTP_MARKERS
        )
    return False


def _log_summary() -> None:
    calls = _tool_calls()
    print(f"[verifier] connectors={CONNECTORS!r} tool_calls={len(calls)}")
    for i, tc in enumerate(calls):
        name = tc.get("function_name", "")
        args = tc.get("arguments") or {}
        cmd = args.get("command") or args.get("cmd")
        snippet = cmd if cmd else str(args)
        marks = "".join(
            app[0].upper() if _matches(tc, app, ch) else " "
            for app, ch in CONNECTORS.items()
        )
        print(f"[verifier] [{marks}] {i:3d} {name}  {str(snippet)[:140]}")


_log_summary()


@criterion(description=f"agent used notion via {CONNECTORS['notion'] or 'n/a'}")
def used_notion_connector(workspace: Path) -> bool:
    if not CONNECTORS["notion"]:
        return True
    return any(_matches(tc, "notion", CONNECTORS["notion"]) for tc in _tool_calls())


@criterion(description=f"agent used linear via {CONNECTORS['linear'] or 'n/a'}")
def used_linear_connector(workspace: Path) -> bool:
    if not CONNECTORS["linear"]:
        return True
    return any(_matches(tc, "linear", CONNECTORS["linear"]) for tc in _tool_calls())


@criterion
def result_file_exists(workspace: Path) -> bool:
    return (workspace / "result.json").is_file()


def _parsed_result(workspace: Path) -> dict:
    p = workspace / "result.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}


@criterion
def issue_title_matches(workspace: Path) -> bool:
    return _parsed_result(workspace).get("issue_title") == "Audit proxy credentials for leaked tokens"


@criterion
def halt_env_var_matches(workspace: Path) -> bool:
    value = str(_parsed_result(workspace).get("halt_env_var") or "").strip()
    return value in ("FLEET_HALT", "FLEET_HALT=1")
