#!/usr/bin/env bash
# Runs svelte-check and writes a per-file error/warning summary to type-check-report.md

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT="$ROOT_DIR/type-check-report.md"

cd "$ROOT_DIR"

bun run svelte-kit sync > /dev/null 2>&1 || true
RAW=$(bunx svelte-check --tsconfig ./tsconfig.json --output machine 2>&1 || true)

RESULT=$(echo "$RAW" | awk '
/^[0-9]+ (ERROR|WARNING)/ {
  sub(/^[0-9]+ /, "")
  type = $1
  if (match($0, /"([^"]+)"/, arr)) {
    file = arr[1]
    if (type == "ERROR") errors[file]++
    else if (type == "WARNING") warnings[file]++
    seen[file] = 1
  }
}
/^[0-9]+ COMPLETED/ {
  match($0, /([0-9]+) ERRORS/, a);   total_errors   = a[1]+0
  match($0, /([0-9]+) WARNINGS/, a); total_warnings = a[1]+0
  match($0, /([0-9]+) FILES_WITH_PROBLEMS/, a); total_files = a[1]+0
}
END {
  print total_errors "\t" total_warnings "\t" total_files
  for (f in seen) {
    print (errors[f]+0) "\t" (warnings[f]+0) "\t" f
  }
}')

TOTAL_ERRORS=$(echo "$RESULT" | head -1 | cut -f1)
TOTAL_WARNINGS=$(echo "$RESULT" | head -1 | cut -f2)
TOTAL_FILES=$(echo "$RESULT" | head -1 | cut -f3)

TABLE=$(echo "$RESULT" | tail -n +2 | sort -t$'\t' -k1 -rn | awk -F'\t' -v root="$ROOT_DIR/" '{
  rel = $3; sub(root, "", rel)
  printf "| [%s](%s) | %d | %d |\n", rel, rel, $1, $2
}')

cat > "$OUTPUT" <<EOF
# Type Check Report

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
