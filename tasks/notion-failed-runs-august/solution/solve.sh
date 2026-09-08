#!/bin/bash
set -e
# Reference answer. The trajectory judge grades real agents; the oracle is not
# gradeable here (no trajectory).
cat <<'ANSWER'
Two runs failed in August 2026: run-007 (amazon-crawler, 2026-08-14) and
run-011 (news-harvester, 2026-08-27).
ANSWER
