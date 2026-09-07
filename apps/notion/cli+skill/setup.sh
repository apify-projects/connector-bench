#!/bin/sh
# See apps/notion/cli/setup.sh — the skill cell uses the same CLI underneath.
set -e
notion-fixtures-probe
if ! ntn pages get "$NOTION_PARENT_PAGE_ID" >/dev/null 2>&1; then
  echo "CONNECTOR_PROBE_FAILED: notion-skill: 'ntn pages get' failed" >&2
  exit 1
fi
echo "cli-probe[notion-skill]: ok"
