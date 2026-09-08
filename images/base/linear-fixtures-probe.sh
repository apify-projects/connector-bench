#!/bin/bash
# Fixture staleness probe shared by the linear cells' setup.sh. Lists the
# workspace's issue labels and requires a manifest label matching the repo's
# fixture hash (created by `connector-evals seed linear`). Aborts the trial
# with a reseed hint on mismatch so sweeps never grade against stale fixtures.
set -eu
: "${LINEAR_API_KEY:?}" "${LINEAR_FIXTURES_HASH:?}"
resp=$(curl -fsS -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ issueLabels(first: 250) { nodes { name } } }"}')
if ! printf '%s' "$resp" | grep -q "connector-evals-manifest-$LINEAR_FIXTURES_HASH"; then
  echo "CONNECTOR_PROBE_FAILED: linear fixtures missing or stale" \
       "(want connector-evals-manifest-$LINEAR_FIXTURES_HASH);" \
       "run 'uv run connector-evals seed linear'" >&2
  exit 1
fi
echo "fixtures-probe[linear]: ok"
