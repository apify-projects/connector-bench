#!/bin/bash
set -e
# Reference answer for linear-backlog-count-needle. The trajectory judge grades real agents; the
# oracle is not gradeable here (no trajectory).
cat <<'EOF'
The 'Scraper Fleet' team has 85 issues in the Backlog state. The single
issue labeled 'security' is 'Audit proxy credentials for leaked tokens'.
EOF
