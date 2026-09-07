#!/bin/bash
# Fixture staleness probe shared by the notion cells' setup.sh. Lists the
# parent page's children (not the search API, whose index lags fresh writes)
# and requires a manifest page matching the repo's fixture hash. Aborts the
# trial with a reseed hint on mismatch so sweeps never grade against stale
# fixtures.
set -eu
: "${NOTION_API_TOKEN:?}" "${NOTION_PARENT_PAGE_ID:?}" "${NOTION_FIXTURES_HASH:?}"
resp=$(curl -fsS \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/blocks/$NOTION_PARENT_PAGE_ID/children?page_size=100")
if ! printf '%s' "$resp" | grep -q "connector-evals-manifest-$NOTION_FIXTURES_HASH"; then
  echo "CONNECTOR_PROBE_FAILED: notion fixtures missing or stale" \
       "(want connector-evals-manifest-$NOTION_FIXTURES_HASH);" \
       "run 'uv run connector-evals seed notion'" >&2
  exit 1
fi
echo "fixtures-probe[notion]: ok"
