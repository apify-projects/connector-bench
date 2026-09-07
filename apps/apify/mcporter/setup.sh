#!/bin/sh
# Register the Apify remote MCP as mcporter server `apify` before the agent
# runs. See images/base/mcporter-probe.sh for the probe contract.
set -e
exec mcporter-probe --name apify --server apify \
  --url https://mcp.apify.com --auth "Bearer $APIFY_TOKEN"
