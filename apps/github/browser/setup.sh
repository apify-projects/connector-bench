#!/bin/sh
# Probe: playwright-mcp starts and lists tools. Browser launch is lazy (first
# tool call), so also assert the chromium download is baked into the image -
# a wrong image would otherwise surface only mid-trial.
set -e
if ! ls /root/.cache/ms-playwright/chromium-*/ >/dev/null 2>&1; then
  echo "CONNECTOR_PROBE_FAILED: github-browser: no chromium under /root/.cache/ms-playwright" >&2
  exit 1
fi
exec mcp-stdio-probe --name browser --timeout 25 --retries 2 -- \
  /usr/local/bin/playwright-mcp --browser chromium --headless --no-sandbox --isolated
