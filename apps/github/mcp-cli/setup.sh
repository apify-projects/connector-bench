#!/bin/sh
# See apps/apify/mcp-cli/setup.sh. No trailing slash on the URL: mcp-cli's
# HTTP transport appends `/mcp` unless the URL already ends with it, and
# `.../mcp/` would get rewritten to `.../mcp/mcp`.
set -e
exec mcp-cli-probe --name github --server github \
  --url https://api.githubcopilot.com/mcp --auth "Bearer $GITHUB_TOKEN"
