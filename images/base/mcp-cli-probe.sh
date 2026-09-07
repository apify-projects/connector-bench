#!/bin/sh
# Probe an mcp-cli (IBM) connector: register the server in
# /app/server_config.json (merged; mcp-cli resolves config from cwd and the
# agent runs in /app) and list its tools. Token is written into the config
# literally - setup_env never reaches the agent env; file exposure matches
# mcpc's ~/.mcpc/sessions.json. Sibling to mcpc-probe.sh; same
# `CONNECTOR_PROBE_FAILED: ...` failure contract.
#
# Usage: mcp-cli-probe --name LABEL --server SERVER --url URL \
#                      --auth "Bearer TOKEN" [--retries N]
#        mcp-cli-probe --name LABEL --server SERVER --command CMD [--retries N]
# --command registers a local stdio server instead of a remote URL. Used by
# the notion cells, whose hosted MCP is OAuth-only.
set -e
RETRIES=2
NAME=mcp-cli
SERVER=
URL=
AUTH=
COMMAND=
CONFIG=/app/server_config.json

while [ $# -gt 0 ]; do
  case "$1" in
    --name)    NAME="$2";    shift 2;;
    --server)  SERVER="$2";  shift 2;;
    --url)     URL="$2";     shift 2;;
    --auth)    AUTH="$2";    shift 2;;
    --command) COMMAND="$2"; shift 2;;
    --retries) RETRIES="$2"; shift 2;;
    *) echo "mcp-cli-probe: unknown arg $1" >&2; exit 2;;
  esac
done

if [ -z "$SERVER" ] || { [ -z "$COMMAND" ] && { [ -z "$URL" ] || [ -z "$AUTH" ]; }; }; then
  echo "mcp-cli-probe: --server plus --url/--auth or --command required" >&2
  exit 2
fi

python3 - "$SERVER" "$URL" "$AUTH" "$COMMAND" "$CONFIG" <<'EOF'
import json, os, shlex, sys
server, url, auth, command, path = sys.argv[1:6]
os.makedirs(os.path.dirname(path), exist_ok=True)
try:
    with open(path) as f:
        cfg = json.load(f)
except Exception:
    cfg = {}
if command:
    argv = shlex.split(command)
    entry = {"command": argv[0], "args": argv[1:]}
else:
    entry = {"url": url, "headers": {"Authorization": auth}}
cfg.setdefault("mcpServers", {})[server] = entry
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
EOF

count_tools() {
  grep -aoE '[0-9]+ Available Tools' | head -1 | cut -d' ' -f1
}

i=0
while [ "$i" -le "$RETRIES" ]; do
  i=$((i + 1))
  n=$(cd /app && mcp-cli tools --server "$SERVER" 2>/dev/null | count_tools)
  if [ "${n:-0}" -ge 1 ]; then
    echo "mcp-cli-probe[$NAME]: ok, $n tools (attempt $i), server '$SERVER' registered"
    exit 0
  fi
  echo "mcp-cli-probe[$NAME]: attempt $i failed" >&2
  sleep 1
done
echo "CONNECTOR_PROBE_FAILED: $NAME-mcp-cli: tools list failed after $i attempts" >&2
exit 1
