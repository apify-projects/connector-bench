#!/bin/sh
# Fixture staleness check, then open the @linear mcpc session before the
# agent runs. See images/base/mcpc-probe.sh for the probe contract.
set -e
linear-fixtures-probe
exec mcpc-probe --name linear --session @linear \
  --url https://mcp.linear.app/mcp --auth "Bearer $LINEAR_API_KEY"
