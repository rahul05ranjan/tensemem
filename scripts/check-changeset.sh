#!/usr/bin/env bash
# Fail unless this branch adds a changes/*.md file, or the title has [no-changeset].
set -euo pipefail

base="${1:-${BASE_SHA:-origin/main}}"
head="${2:-${HEAD_SHA:-HEAD}}"
title="${PR_TITLE:-}"

if printf '%s' "${title}" | grep -Fqi -- '[no-changeset]'; then
  echo "[no-changeset] in PR title; skipping changes/ check."
  exit 0
fi

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
  echo "::error::Add changes/<slug>.md, or put [no-changeset] in the PR title."
  exit 1
fi
