#!/bin/bash
# Stdio shim for https://mcp.linear.app/mcp. See apify-mcp-proxy.sh for the
# pattern (harbor's MCPServerConfig has no `headers` field); Linear's hosted
# MCP accepts a personal API key as a bearer token, so mcp-remote just
# injects the header.
#
# Token resolution: prefer $LINEAR_API_KEY (ad-hoc debugging); else read
# /etc/linear-mcp.token (written by apps/linear/mcp/setup.sh, kept out of the
# agent's env so the agent can't `echo $LINEAR_API_KEY` it into the
# trajectory).
#
# stderr is redacted (strip lin_api_* / lin_oauth_* tokens) and tee'd to
# /logs/agent/linear-mcp-proxy.stderr, matching the other proxies.
set -eu
TOKEN_FILE=/etc/linear-mcp.token
if [ -z "${LINEAR_API_KEY:-}" ] && [ -r "$TOKEN_FILE" ]; then
  LINEAR_API_KEY=$(cat "$TOKEN_FILE")
fi
: "${LINEAR_API_KEY:?LINEAR_API_KEY env var or $TOKEN_FILE required}"
LOG=/logs/agent/linear-mcp-proxy.stderr
mcp-remote https://mcp.linear.app/mcp --header "Authorization: Bearer $LINEAR_API_KEY" \
  2> >(sed -E "s/lin_(api|oauth)_[A-Za-z0-9]+/lin_\1_REDACTED/g" \
       | tee -a "$LOG" 2>/dev/null >&2)
