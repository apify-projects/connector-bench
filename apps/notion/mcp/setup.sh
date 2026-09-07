#!/bin/sh
# Fixture staleness check, then token stash + MCP stdio probe (see
# apps/apify/mcp/setup.sh for the stash/probe rationale). Non-zero exit
# aborts the trial before any agent tokens are billed.
set -e
notion-fixtures-probe
TOKEN_FILE=/etc/notion-mcp.token
printf '%s' "$NOTION_API_TOKEN" > "$TOKEN_FILE"
chmod 400 "$TOKEN_FILE"
unset NOTION_API_TOKEN
exec mcp-stdio-probe --name notion --timeout 25 --retries 2 -- /usr/local/bin/notion-mcp-proxy
