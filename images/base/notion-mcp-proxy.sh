#!/bin/bash
# Stdio shim for the official @notionhq/notion-mcp-server. Unlike the apify /
# github proxies this spawns a local server rather than mcp-remote; the wrapper
# exists to read the token from /etc/notion-mcp.token (written by
# apps/notion/mcp/setup.sh, kept out of the agent's env so the agent can't
# `echo $NOTION_API_TOKEN` it into the trajectory).
#
# stderr is redacted (strip ntn_/secret_ tokens) and tee'd to
# /logs/agent/notion-mcp-proxy.stderr, matching the other proxies.
set -eu
TOKEN_FILE=/etc/notion-mcp.token
if [ -z "${NOTION_API_TOKEN:-}" ] && [ -r "$TOKEN_FILE" ]; then
  NOTION_API_TOKEN=$(cat "$TOKEN_FILE")
fi
: "${NOTION_API_TOKEN:?NOTION_API_TOKEN env var or $TOKEN_FILE required}"
LOG=/logs/agent/notion-mcp-proxy.stderr
NOTION_TOKEN="$NOTION_API_TOKEN" notion-mcp-server \
  2> >(sed -E "s/(ntn_|secret_)[A-Za-z0-9]+/\1REDACTED/g" \
       | tee -a "$LOG" 2>/dev/null >&2)
