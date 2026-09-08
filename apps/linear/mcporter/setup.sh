#!/bin/sh
# See apps/linear/mcpc/setup.sh.
set -e
linear-fixtures-probe
exec mcporter-probe --name linear --server linear \
  --url https://mcp.linear.app/mcp --auth "Bearer $LINEAR_API_KEY"
