#!/usr/bin/env bash
# Fail unless this branch adds at least one changes/*.md file (not README).
set -euo pipefail

base="${1:-${BASE_SHA:-origin/main}}"
head="${2:-${HEAD_SHA:-HEAD}}"
labels="${LABELS:-}"

case ",${labels}," in
  *,skip-changeset,*)
    echo "skip-changeset label present; allowing empty changes/."
    exit 0
    ;;
esac

added=$(git diff --name-only --diff-filter=A "${base}...${head}" -- changes || true)
count=0
while IFS= read -r path; do
  [ -z "${path}" ] && continue
  name=$(basename "${path}")
  if [ "${name}" = "README.md" ]; then
    continue
  fi
  if [[ "${name}" == *.md ]]; then
    echo "changeset: ${path}"
    count=$((count + 1))
  fi
done <<< "${added}"

if [ "${count}" -eq 0 ]; then
  echo "::error::Add a new file under changes/ (see changes/README.md), or label the PR skip-changeset."
  exit 1
fi
