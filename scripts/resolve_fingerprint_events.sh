#!/usr/bin/env bash
#
# Batch resolve fingerprint info events that are not actual errors
#

set -e

cd "$(dirname "$0")/.."

echo "Resolving fingerprint info-level events..."

# Fingerprint events (info level, not actual errors)
FINGERPRINT_ISSUES=(
  "6983203140"  # PYTHON-W: Fingerprinted FORD_F_150_LIGHTNING_MK1
  "6983699090"  # PYTHON-X: Fingerprinted FORD_MAVERICK_MK1
  "6974623624"  # PYTHON-A: Fingerprinted FORD_MUSTANG_MACH_E_MK1
  "6982816991"  # PYTHON-S: Fingerprinted FORD_ESCAPE_MK4
  "6972283075"  # PYTHON-2: Fingerprinted FORD_F_150_MK14
  "6983109282"  # PYTHON-V: Fingerprinted HYUNDAI_TUCSON_4TH_GEN
)

# Qt UI status reports (info level)
QT_UI_ISSUES=(
  "6977493386"  # PYTHON-C: Qt UI - UNKNOWN - unknown
)

ALL_ISSUES=("${FINGERPRINT_ISSUES[@]}" "${QT_UI_ISSUES[@]}")

for issue_id in "${ALL_ISSUES[@]}"; do
  echo "Resolving issue $issue_id..."
  sentry-cli issues resolve -i "$issue_id" || echo "Failed to resolve $issue_id (may already be resolved)"
done

echo "✓ Finished resolving info-level events"

