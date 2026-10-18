#!/usr/bin/env bash
# Require exactly one risk tag in the PR title.
set -euo pipefail

title="${PR_TITLE:-}"
if [ -z "${title}" ]; then
  echo "::error::PR title is empty."
  exit 1
fi

echo "PR title: ${title}"

risks=0
for tag in '[low-risk]' '[medium-risk]' '[high-risk]'; do
  if printf '%s' "${title}" | grep -Fqi -- "${tag}"; then
    echo "risk tag: ${tag}"
    risks=$((risks + 1))
  fi
done

if [ "${risks}" -eq 0 ]; then
  echo "::error::PR title must include one of [low-risk], [medium-risk], or [high-risk]."
  exit 1
fi
if [ "${risks}" -gt 1 ]; then
  echo "::error::PR title must include only one risk tag."
  exit 1
fi
