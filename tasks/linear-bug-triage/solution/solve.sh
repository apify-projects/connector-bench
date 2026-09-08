#!/bin/bash
set -e
# Reference answer for linear-bug-triage. The trajectory judge grades real
# agents; the oracle is not gradeable here (no trajectory).
cat <<'EOF'
The 'Scraper Fleet' team has 4 bug-labeled issues that are not completed or
canceled. Urgent: 'amazon-crawler hits captcha wall on product pages' and
'google-maps-scraper returns stale opening hours'.
EOF
