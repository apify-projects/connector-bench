#!/bin/sh
# See apps/notion/mcpc/setup.sh.
set -e
notion-fixtures-probe
TOKEN_FILE=/etc/notion-mcp.token
printf '%s' "$NOTION_API_TOKEN" > "$TOKEN_FILE"
chmod 400 "$TOKEN_FILE"
unset NOTION_API_TOKEN
exec mcporter-probe --name notion --server notion \
  --command /usr/local/bin/notion-mcp-proxy
