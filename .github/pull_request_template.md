## What

<!-- Bullet list of concrete changes in this PR. -->

-

## Why

<!-- The problem or decision this addresses. -->

-

## Docs

<!-- What docs/ADRs/README changed, or "none needed" with a one-line reason. -->

-

## Title

Must include one risk tag: `[low-risk]`, `[medium-risk]`, or `[high-risk]`.
Use `[no-changeset]` in the title only when no `changes/` file is needed.

## Changeset

- [ ] Added `changes/<slug>.md`, or the title includes `[no-changeset]` (see [changes/README.md](../changes/README.md)).
- [ ] Do not update the README status line for internal work.

## Test plan

- [ ] `uv run ruff check . && uv run ruff format --check .`
- [ ] `uv run pyright`
- [ ] `uv run pytest`
