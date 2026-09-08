#!/bin/bash
set -e
# Reference answer for linear-release-blockers. The trajectory judge grades real agents; the
# oracle is not gradeable here (no trajectory).
cat <<'EOF'
Two issues still block 'Ship crawler v2': 'Sign proxy vendor contract'
(In Progress) and 'Load-test proxy failover' (Todo). The third blocker,
'Update scraper base image for v2', is Done.
EOF
