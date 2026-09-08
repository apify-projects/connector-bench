#!/bin/sh
# Fixture staleness check + linear CLI connectivity probe (the CLI reads
# LINEAR_API_KEY from the env). Non-zero exit aborts the trial.
set -e
linear-fixtures-probe
if ! linear auth whoami >/dev/null 2>&1; then
  echo "CONNECTOR_PROBE_FAILED: linear-cli: 'linear auth whoami' failed" >&2
  exit 1
fi
echo "cli-probe[linear]: ok"
