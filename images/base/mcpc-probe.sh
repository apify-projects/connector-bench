#!/bin/sh
# Probe an mcpc connector: connect a named session, list its tools, leave the
# session open on success (so the agent inherits an authenticated bridge).
# Sibling to mcp-stdio-probe.py; same `CONNECTOR_PROBE_FAILED: ...` failure
# contract. Used by apps/{apify,github}/mcpc/setup.sh.
#
# Usage: mcpc-probe --name LABEL --session @SESSION --url URL \
#                   --auth "Bearer TOKEN" [--retries N]
#        mcpc-probe --name LABEL --session @SESSION --command CMD [--retries N]
# --command connects a local stdio server instead of a remote URL (written as
# a config-file entry, mcpc's stdio connect format). Used by the notion cells,
# whose hosted MCP is OAuth-only.
set -e
RETRIES=2
NAME=mcpc
SESSION=
URL=
AUTH=
COMMAND=

while [ $# -gt 0 ]; do
  case "$1" in
    --name)    NAME="$2";    shift 2;;
    --session) SESSION="$2"; shift 2;;
    --url)     URL="$2";     shift 2;;
    --auth)    AUTH="$2";    shift 2;;
    --command) COMMAND="$2"; shift 2;;
    --retries) RETRIES="$2"; shift 2;;
    *) echo "mcpc-probe: unknown arg $1" >&2; exit 2;;
  esac
done

if [ -z "$SESSION" ] || { [ -z "$COMMAND" ] && { [ -z "$URL" ] || [ -z "$AUTH" ]; }; }; then
  echo "mcpc-probe: --session plus --url/--auth or --command required" >&2
  exit 2
fi

if [ -n "$COMMAND" ]; then
  CFG="/etc/mcpc-$NAME.json"
  python3 - "$NAME" "$COMMAND" "$CFG" <<'EOF'
import json, shlex, sys
name, command, path = sys.argv[1:4]
argv = shlex.split(command)
with open(path, "w") as f:
    json.dump({"mcpServers": {name: {"command": argv[0], "args": argv[1:]}}}, f)
EOF
fi

count_tools() {
  python3 -c 'import sys,json
try: d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)
except Exception: print(0)'
}

attempt() {
  if [ -n "$COMMAND" ]; then
    mcpc connect "$CFG:$NAME" "$SESSION" >/dev/null 2>&1 || return 1
  else
    mcpc connect "$URL" "$SESSION" --header "Authorization: $AUTH" >/dev/null 2>&1 || return 1
  fi
  n=$(mcpc --json "$SESSION" tools-list 2>/dev/null | count_tools)
  [ "${n:-0}" -ge 1 ] && echo "$n"
}

i=0
while [ "$i" -le "$RETRIES" ]; do
  i=$((i + 1))
  if n=$(attempt); then
    echo "mcpc-probe[$NAME]: ok, $n tools (attempt $i), $SESSION left open for agent"
    exit 0
  fi
  mcpc close "$SESSION" >/dev/null 2>&1 || true
  echo "mcpc-probe[$NAME]: attempt $i failed" >&2
  sleep 1
done
echo "CONNECTOR_PROBE_FAILED: $NAME-mcpc: connect or tools-list failed after $i attempts" >&2
exit 1
