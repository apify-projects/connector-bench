#!/bin/sh
# Fixture staleness check, key stash for linear-mcp-proxy (see
# apps/apify/mcp/setup.sh for the probe rationale), then probe the stdio
# proxy. Non-zero exit aborts the trial.
set -e
linear-fixtures-probe
TOKEN_FILE=/etc/linear-mcp.token
printf '%s' "$LINEAR_API_KEY" > "$TOKEN_FILE"
chmod 400 "$TOKEN_FILE"
unset LINEAR_API_KEY
exec mcp-stdio-probe --name linear --timeout 25 --retries 2 -- /usr/local/bin/linear-mcp-proxy
