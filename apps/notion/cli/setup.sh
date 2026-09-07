#!/bin/sh
# Fixture staleness check + ntn connectivity probe (ntn reads NOTION_API_TOKEN
# from the env; probe the parent page, not v1/users, which needs the
# "read user information" capability integrations don't get by default).
# Non-zero exit aborts the trial.
set -e
notion-fixtures-probe
if ! ntn pages get "$NOTION_PARENT_PAGE_ID" >/dev/null 2>&1; then
  echo "CONNECTOR_PROBE_FAILED: notion-cli: 'ntn pages get' failed" >&2
  exit 1
fi
echo "cli-probe[notion]: ok"
