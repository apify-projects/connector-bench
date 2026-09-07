#!/bin/bash
set -e
# Reference answer for notion-scraper-inventory. The trajectory judge grades
# real agents; the oracle is not gradeable here (no trajectory).
cat <<'EOF'
The 'Scraper Inventory' page lists 5 scrapers in total. Deprecated:
amazon-crawler (owner Bob) and jobs-radar (owner Dana).
EOF
