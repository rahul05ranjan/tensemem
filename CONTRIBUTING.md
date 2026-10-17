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
```

## Workflow

- `main` is protected. All changes go through pull requests.
- Keep each PR focused on one change, and describe what changed and why.
- Significant design changes need an architecture decision record in `docs/adr/`.
- Write commit messages in the imperative mood, for example "Add predicate registry".
- Agents and editors should follow the project rules in [`.cursor/rules/`](.cursor/rules/) (short PRs, docs in the same change, vendor-neutral public docs).
