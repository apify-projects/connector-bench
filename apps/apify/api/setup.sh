#!/bin/sh
# Write the auth header file and probe the REST API with it. Probe is inline
# (no image-side script, so no dirhash change); same `CONNECTOR_PROBE_FAILED`
# contract as images/base/*-probe.sh.
set -e
mkdir -p /root/.api-headers
printf 'Authorization: Bearer %s\n' "$APIFY_TOKEN" > /root/.api-headers/apify
code=$(curl -s -o /dev/null -w '%{http_code}' -H @/root/.api-headers/apify \
  https://api.apify.com/v2/users/me)
if [ "$code" != "200" ]; then
  echo "CONNECTOR_PROBE_FAILED: apify-api: /v2/users/me returned $code" >&2
  exit 1
fi
echo "api-probe[apify]: ok, /v2/users/me 200"
