# Changes

Every pull request must add **one new file** in this folder, unless the title
contains `[no-changeset]`. That file is the durable record of what landed. Do
not update the README status line for internal slices.

## PR title

The title must include **exactly one** risk tag:

```
[low-risk] Require a changeset file on every pull request
[medium-risk] Add a pure resolver for the fact decision table
[high-risk] Change how ACTIVE facts are stored
```

To skip a changeset (docs-only, CI pin, empty rebase), add `[no-changeset]`:

```
[low-risk] [no-changeset] Pin setup-uv action
```

Without a risk tag, CI fails and the PR cannot merge.

## File name

`kebab-case.md`, unique, describing the change:

```
changes/add-resolver.md
changes/require-changeset-on-prs.md
```

Do not edit or delete existing files in a later PR unless you are fixing a typo
in a fragment that has not been released yet.

## File body

```markdown
## What

- One or two bullets.

## Why

One or two sentences.
```
