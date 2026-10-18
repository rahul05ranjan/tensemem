# Changes

Every pull request must add **one new file** in this folder. That file is the
durable record of what landed. Do not update the README status line for
internal slices.

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

## Skip

Only if the PR is an empty rebase or CI-only pin with **no product change**.
Add the `skip-changeset` label and say why in the PR body.
