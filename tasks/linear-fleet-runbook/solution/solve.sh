#!/bin/bash
set -e
# Reference answer for linear-fleet-runbook. The trajectory judge grades real agents; the
# oracle is not gradeable here (no trajectory).
cat <<'EOF'
Per the 'Fleet Runbook' document: proxy credential rotation runs every
6 hours, and setting FLEET_HALT=1 halts the whole fleet.
EOF
