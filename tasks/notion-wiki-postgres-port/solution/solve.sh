#!/bin/bash
set -e
# Reference answer. The trajectory judge grades real agents; the oracle is not
# gradeable here (no trajectory).
cat <<'ANSWER'
Staging Postgres listens on port 6543 (via pgbouncer). Nightly backups run at
03:30 UTC. (Engineering Wiki > Runbooks > Postgres Runbook)
ANSWER
