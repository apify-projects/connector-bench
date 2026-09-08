#!/bin/bash
set -e
# Reference answer for linear-vendor-decision. The trajectory judge grades real agents; the
# oracle is not gradeable here (no trajectory).
cat <<'EOF'
The final decision on 'Choose proxy vendor for the fleet' is NimbusProxy
at $2.40/GB (HydraNet failed geo-coverage, GridRelay was rejected by
finance).
EOF
