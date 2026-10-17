# Contributing to TenseMem

## Setup

TenseMem uses [uv](https://docs.astral.sh/uv/) for environments and dependencies.

```bash
git clone https://github.com/tensemem/tensemem.git
cd tensemem
uv sync                      # creates .venv with dev tools
uv run pre-commit install    # lint and format on every commit
```

## Checks

CI runs these on every pull request; run them locally before pushing:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
uvx codespell --skip="*.lock,.git,uv.lock" --ignore-words-list="tensemem"
```

Every PR also gets free automated review gates:

| Check | What it does |
|---|---|
| **CI** | Ruff (with inline annotations), format, pyright, pytest, package build |
| **PR quality** | Requires `## What` / `## Why` / `## Docs` in the body; fails oversized diffs (>1000 lines unless labeled `large-pr`); actionlint posts workflow findings as review comments; gitleaks scans for secrets |
| **CodeQL** | Security analysis for Python and GitHub Actions (free on public repos) |

Optional AI review (also free for public repos): install [CodeRabbit](https://github.com/apps/coderabbitai) on the `tensemem` org if you want natural-language PR review on top of the gates above.

In branch protection, require at least: `Lint and type-check`, `PR description and size`, and `Analyze (python)`.

## Workflow

- `main` is protected. All changes go through pull requests.
- Keep each PR focused on one change, and describe what changed and why. Use the pull request template.
- Significant design changes need an architecture decision record in `docs/adr/`.
- Write commit messages in the imperative mood, for example "Add predicate registry".
- Agents and editors should follow the project rules in [`.cursor/rules/`](.cursor/rules/) (short PRs, docs in the same change, vendor-neutral public docs).
