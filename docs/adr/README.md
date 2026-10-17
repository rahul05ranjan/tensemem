# Architecture Decision Records

Each record captures one significant design decision: the context, what we chose, what we rejected, and when we should revisit it. Records are immutable once accepted; to change a decision, add a new record that supersedes the old one.

| # | Decision | Status |
|---|---|---|
| [0001](0001-event-sourced-episodes.md) | Raw messages are an append-only log; facts are a rebuildable projection | Accepted |
| [0002](0002-llm-proposes-engine-decides.md) | The LLM proposes typed operations; deterministic code applies them | Accepted |
| [0003](0003-sqlite-single-writer.md) | SQLite is the default store, with one writer per process | Accepted |
| [0004](0004-optional-embeddings.md) | Embeddings are optional; full-text search is the default retrieval path | Accepted |
| [0005](0005-bitemporal-facts.md) | Facts track both valid time and recorded time | Accepted |

## Template

```markdown
# NNNN. Title

- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD

## Context
## Decision
## Alternatives considered
## Consequences
## Revisit when
```
