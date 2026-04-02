#!/bin/zsh
set -euo pipefail

if [[ $# -lt 5 ]]; then
  cat <<'EOF'
Usage:
  run_single_day_shift.sh <YYYYMMDD> <SHIFT_CODE> <SHIFT_NAME> <SCREENSHOT_PATH> <EMPLOYEE_LABEL::EMPNO> [<EMPLOYEE_LABEL::EMPNO> ...]

Example:
  run_single_day_shift.sh 20260410 b0023 基金會常日班 \
    artifacts/screenshots/kuang_shuqi_20260410_b0023_verified.png \
    '李冠葦(101)::0000000005' \
    '陳淑錡(102)::0000000001'

Notes:
  - Date must be YYYYMMDD.
  - Shift time comes from SHIFT_CODE in Aurora HR.
  - If you need arbitrary time ranges instead of a normal shift code, use the ba000 workflow instead.
EOF
  exit 1
fi

DATE_ARG="$1"
SHIFT_CODE="$2"
SHIFT_NAME="$3"
SCREENSHOT_PATH="$4"
shift 4

CMD=(
  python3
  /Users/Shared/codex-skills/aurora-hr-schedule-operator/scripts/apply_single_day_shift.py
  --date "$DATE_ARG"
  --shift-code "$SHIFT_CODE"
  --shift-name "$SHIFT_NAME"
  --screenshot "$SCREENSHOT_PATH"
)

for employee in "$@"; do
  CMD+=(--employee "$employee")
done

exec "${CMD[@]}"
