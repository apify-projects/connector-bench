#!/bin/sh
# See apps/linear/mcpc/setup.sh. No `#/mcp` fragment hack needed (unlike
# apify): the URL already ends in /mcp, so mcp-cli's path rewrite is a no-op.
set -e
linear-fixtures-probe
exec mcp-cli-probe --name linear --server linear \
  --url https://mcp.linear.app/mcp --auth "Bearer $LINEAR_API_KEY"
