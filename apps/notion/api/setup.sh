#!/bin/sh
# See apps/apify/api/setup.sh. Notion also requires a Notion-Version header.
set -e
notion-fixtures-probe
mkdir -p /root/.api-headers
{
  printf 'Authorization: Bearer %s\n' "$NOTION_API_TOKEN"
  printf 'Notion-Version: 2022-06-28\n'
} > /root/.api-headers/notion
code=$(curl -s -o /dev/null -w '%{http_code}' -H @/root/.api-headers/notion \
  https://api.notion.com/v1/users/me)
if [ "$code" != "200" ]; then
  echo "CONNECTOR_PROBE_FAILED: notion-api: /v1/users/me returned $code" >&2
  exit 1
fi
echo "api-probe[notion]: ok, /v1/users/me 200"
