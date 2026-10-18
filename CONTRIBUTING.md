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
| **PR quality** | Requires a risk tag in the title (`[low-risk]` / `[medium-risk]` / `[high-risk]`); `## What` / `## Why` / `## Docs`; a new `changes/<slug>.md` file (or `[no-changeset]` in the title); fails oversized diffs (>1000 lines unless labeled `large-pr`); actionlint; gitleaks |
| **CodeQL** | Security analysis for Python and GitHub Actions (free on public repos) |

We do **not** depend on third-party AI review apps (many look free then push a paid trial). Quality comes from the gates above plus human review.

In branch protection, require at least: `Lint and type-check`, `PR description and size`, and `Analyze (python)`.

## Workflow

- `main` is protected. All changes go through pull requests.
- Keep each PR focused on one change, and describe what changed and why. Use the pull request template.
- Title must include `[low-risk]`, `[medium-risk]`, or `[high-risk]`.
- Add a changeset file under [changes/](changes/), or put `[no-changeset]` in the title. Do not bump the README status line for internal work.
- Significant design changes need an architecture decision record in `docs/adr/`.
- Write commit messages in the imperative mood, for example "Add predicate registry".
- Agents and editors should follow the project rules in [`.cursor/rules/`](.cursor/rules/) (short PRs, docs in the same change, vendor-neutral public docs).
