#!/bin/sh
# See apps/apify/api/setup.sh.
set -e
mkdir -p /root/.api-headers
{
  printf 'Authorization: Bearer %s\n' "$GITHUB_TOKEN"
  printf 'Accept: application/vnd.github+json\n'
  printf 'X-GitHub-Api-Version: 2022-11-28\n'
} > /root/.api-headers/github
code=$(curl -s -o /dev/null -w '%{http_code}' -H @/root/.api-headers/github \
  https://api.github.com/user)
if [ "$code" != "200" ]; then
  echo "CONNECTOR_PROBE_FAILED: github-api: /user returned $code" >&2
  exit 1
fi
echo "api-probe[github]: ok, /user 200"
