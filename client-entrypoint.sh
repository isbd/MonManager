#!/bin/sh
set -eu

ID="${CRAFTOS_ID:-0}"
WIDTH="${CRAFTOS_WIDTH:-51}"
HEIGHT="${CRAFTOS_HEIGHT:-19}"

mkdir -p /craftos-data/config
cat > "/craftos-data/config/${ID}.json" <<EOF
{
  "computerWidth": ${WIDTH},
  "computerHeight": ${HEIGHT}
}
EOF

exec craftos --id "$ID" --data-dir /craftos-data "$@"