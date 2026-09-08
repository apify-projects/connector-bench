#!/bin/bash
set -e
# Reference answer for cross-weekly-ops-brief. The trajectory judge grades real
# agents; the oracle is not gradeable here (no trajectory).
cat <<'EOF'
1. Linear: 4 open bug-labeled issues; urgent: 'amazon-crawler hits captcha
   wall on product pages', 'google-maps-scraper returns stale opening hours'.
2. Notion: failed in August 2026: run-007 (amazon-crawler, 2026-08-14) and
   run-011 (news-harvester, 2026-08-27).
3. GitHub: PR #50863 "fix: standardize 'MS Teams' to 'Microsoft Teams' across
   docs" is merged.
4. Apify: apify/website-content-crawler pricing model is FREE.
EOF
