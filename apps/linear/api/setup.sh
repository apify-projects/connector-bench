#!/bin/sh
# See apps/apify/api/setup.sh. Linear is GraphQL-only: personal API keys go
# in a bare Authorization header (no Bearer prefix).
set -e
linear-fixtures-probe
mkdir -p /root/.api-headers
printf 'Authorization: %s\n' "$LINEAR_API_KEY" > /root/.api-headers/linear
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H @/root/.api-headers/linear \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ viewer { id } }"}' https://api.linear.app/graphql)
if [ "$code" != "200" ]; then
  echo "CONNECTOR_PROBE_FAILED: linear-api: viewer query returned $code" >&2
  exit 1
fi
echo "api-probe[linear]: ok, viewer query 200"
