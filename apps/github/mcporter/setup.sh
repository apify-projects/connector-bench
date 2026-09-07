#!/bin/sh
# See apps/apify/mcporter/setup.sh.
set -e
exec mcporter-probe --name github --server github \
  --url https://api.githubcopilot.com/mcp/ --auth "Bearer $GITHUB_TOKEN"
