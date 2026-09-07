#!/bin/sh
# Probe a mcporter connector: register the server in ~/.mcporter/mcporter.json
# (merged, so multi-app tasks can register several servers) and list its tools.
# Token is written into the config literally - setup_env never reaches the
# agent env; file exposure matches mcpc's ~/.mcpc/sessions.json. Sibling to
# mcpc-probe.sh; same `CONNECTOR_PROBE_FAILED: ...` failure contract.
#
# Usage: mcporter-probe --name LABEL --server SERVER --url URL \
#                       --auth "Bearer TOKEN" [--retries N]
set -e
RETRIES=2
NAME=mcporter
SERVER=
URL=
AUTH=

while [ $# -gt 0 ]; do
  case "$1" in
    --name)    NAME="$2";    shift 2;;
    --server)  SERVER="$2";  shift 2;;
    --url)     URL="$2";     shift 2;;
    --auth)    AUTH="$2";    shift 2;;
    --retries) RETRIES="$2"; shift 2;;
    *) echo "mcporter-probe: unknown arg $1" >&2; exit 2;;
  esac
done

if [ -z "$SERVER" ] || [ -z "$URL" ] || [ -z "$AUTH" ]; then
  echo "mcporter-probe: --server, --url, --auth required" >&2
  exit 2
fi

python3 - "$SERVER" "$URL" "$AUTH" <<'EOF'
import json, os, sys
server, url, auth = sys.argv[1:4]
path = os.path.expanduser("~/.mcporter/mcporter.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
try:
    with open(path) as f:
        cfg = json.load(f)
except Exception:
    cfg = {}
cfg.setdefault("mcpServers", {})[server] = {
    "baseUrl": url,
    "headers": {"Authorization": auth},
}
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
EOF

count_tools() {
  python3 -c 'import sys,json
try:
    d = json.load(sys.stdin)
    print(len(d.get("tools") or []) if d.get("status") == "ok" else 0)
except Exception: print(0)'
}

i=0
while [ "$i" -le "$RETRIES" ]; do
  i=$((i + 1))
  n=$(mcporter list "$SERVER" --json 2>/dev/null | count_tools)
  if [ "${n:-0}" -ge 1 ]; then
    echo "mcporter-probe[$NAME]: ok, $n tools (attempt $i), server '$SERVER' registered"
    exit 0
  fi
  echo "mcporter-probe[$NAME]: attempt $i failed" >&2
  sleep 1
done
echo "CONNECTOR_PROBE_FAILED: $NAME-mcporter: tools list failed after $i attempts" >&2
exit 1
