#!/bin/bash
set -e
# Reference answer. The trajectory judge grades real agents; the oracle is not
# gradeable here (no trajectory).
cat <<'ANSWER'
The Status property allows three values: success, failed, cancelled (cancelled
is defined in the schema but unused by any row).
ANSWER
