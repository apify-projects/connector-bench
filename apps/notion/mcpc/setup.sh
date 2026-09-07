#!/bin/sh
# Fixture staleness check, token stash for notion-mcp-proxy (see
# apps/notion/mcp/setup.sh), then open the @notion mcpc session over stdio.
set -e
notion-fixtures-probe
TOKEN_FILE=/etc/notion-mcp.token
printf '%s' "$NOTION_API_TOKEN" > "$TOKEN_FILE"
chmod 400 "$TOKEN_FILE"
unset NOTION_API_TOKEN
exec mcpc-probe --name notion --session @notion \
  --command /usr/local/bin/notion-mcp-proxy
