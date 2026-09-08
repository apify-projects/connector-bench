#!/bin/sh
# See apps/linear/cli/setup.sh - the skill cell uses the same CLI underneath.
set -e
linear-fixtures-probe
if ! linear auth whoami >/dev/null 2>&1; then
  echo "CONNECTOR_PROBE_FAILED: linear-skill: 'linear auth whoami' failed" >&2
  exit 1
fi
echo "cli-probe[linear-skill]: ok"
