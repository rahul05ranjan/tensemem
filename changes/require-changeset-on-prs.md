## What

- Require a new `changes/<slug>.md` file on every PR, unless the title has `[no-changeset]`.
- Require exactly one of `[low-risk]`, `[medium-risk]`, or `[high-risk]` in the PR title.
- Stop using the README status line as a running changelog.

## Why

Each merge should leave a durable, reviewable record of what changed, and the
title should say how risky the change is, without churning the public README.
