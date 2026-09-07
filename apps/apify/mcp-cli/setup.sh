#!/bin/sh
# Register the Apify remote MCP as mcp-cli server `apify` before the agent
# runs. See images/base/mcp-cli-probe.sh for the probe contract.
#
# The `#/mcp` fragment defeats mcp-cli's hardcoded path rewrite: its HTTP
# transport appends `/mcp` to any URL not already ending in it
# (chuk_tool_processor http_streamable_transport), but Apify serves MCP at the
# root. The fragment satisfies the endswith check and is stripped before the
# request goes out.
set -e
exec mcp-cli-probe --name apify --server apify \
  --url 'https://mcp.apify.com/#/mcp' --auth "Bearer $APIFY_TOKEN"
