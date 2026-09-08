#!/bin/bash
set -e
cat <<'EOF' > /app/result.json
{"issue_title": "Audit proxy credentials for leaked tokens", "halt_env_var": "FLEET_HALT"}
EOF
