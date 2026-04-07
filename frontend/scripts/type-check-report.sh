#!/usr/bin/env bash
# Runs svelte-check and writes a per-file error/warning summary to type-check-report.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT="$ROOT_DIR/type-check-report.md"

cd "$ROOT_DIR"

RAW=$(bun run check 2>&1 || true)

TOTALS=$(echo "$RAW" | grep -E '^[0-9]+ COMPLETED' | head -1)
TOTAL_ERRORS=$(echo "$TOTALS" | grep -oP '\d+(?= ERRORS)' || echo 0)
TOTAL_WARNINGS=$(echo "$TOTALS" | grep -oP '\d+(?= WARNINGS)' || echo 0)
TOTAL_FILES=$(echo "$TOTALS" | grep -oP '\d+(?= FILES_WITH_PROBLEMS)' || echo 0)

TABLE=$(echo "$RAW" | grep -E '^[0-9]+ (ERROR|WARNING)' | sed 's/^[0-9]* //' | awk '
{
  type=$1
  match($0, /"([^"]+)"/, arr)
  file=arr[1]
  if (file != "") {
    if (type == "ERROR") errors[file]++
    else if (type == "WARNING") warnings[file]++
    seen[file]=1
  }
}
END {
  for (f in seen) {
    print (errors[f]+0) "\t" (warnings[f]+0) "\t" f
  }
}' | sort -t$'\t' -k1 -rn | awk -F'\t' '{printf "| `%s` | %d | %d |\n", $3, $1, $2}')

DATE=$(date +%Y-%m-%d)
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

cat > "$OUTPUT" <<EOF
# Type Check Report

Generated: $DATE
Branch: \`$BRANCH\`
Command: \`bun run check\`

## Summary

| | Count |
|--|------:|
| Errors | $TOTAL_ERRORS |
| Warnings | $TOTAL_WARNINGS |
| Files with problems | $TOTAL_FILES |

## Per-file breakdown

| File | Errors | Warnings |
|------|-------:|--------:|
$TABLE
EOF

echo "Written to $OUTPUT"
echo "  Errors:   $TOTAL_ERRORS"
echo "  Warnings: $TOTAL_WARNINGS"
echo "  Files:    $TOTAL_FILES"
