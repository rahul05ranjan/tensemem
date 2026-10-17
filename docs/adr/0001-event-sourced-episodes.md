# 0001. Raw messages are an append-only log; facts are a rebuildable projection

- Status: Accepted
- Date: 2026-10-17

## Context

TenseMem turns conversations into facts using an LLM. Extraction quality will improve over time (better prompts, better models, better normalization), and early versions will make mistakes. If we store only the extracted facts, every past mistake is permanent and every improvement only helps future messages.

We also need provenance: for any fact, users must be able to see which message produced it.

## Decision

1. Every input is stored first as an **episode**: the raw message, its role, its scope, the time it happened (`occurred_at`), and the time we received it (`ingested_at`).
2. **Facts are a projection of episodes.** They can be deleted and rebuilt at any time by replaying episodes through the current pipeline (`rebuild()`).
3. **Explicit writes are episodes too.** Calls like `set()`, `retract()` and `register_predicate()` are recorded as episodes of kind `explicit_op` with a structured payload. Without this, a rebuild would silently drop everything a developer wrote directly.
4. Ingest writes the episode and its processing job in **one transaction** (an outbox). A message is never accepted without being queued, and never queued without being stored.
5. Ingest is **idempotent**: `(scope, content_hash, occurred_at)` is unique, so retried `add()` calls don't create duplicates.
6. Every fact keeps an `EVIDENCED_BY` link to the episode or episodes that support it.
7. LLM responses are cached by `(model, prompt hash)`. Replaying with the same model and prompt version reproduces the same facts at no cost; replaying with a new model is the intended way to upgrade.

The log is append-only with **one exception: erasure**. `forget()` hard-deletes episodes and everything derived from them, leaving only a content-free tombstone. Privacy law outranks log purity.

## Alternatives considered

- **Store facts only (the PDF's MVP).** Simplest, but extraction mistakes become permanent, there is no provenance, and model upgrades can't fix old data.
- **Store facts plus a free-text "source" field.** Gives provenance but not rebuildability, and the source text drifts from what was actually ingested.
- **Full event sourcing of every internal state change as the source of truth.** More general, but much more complex. We keep a `fact_events` audit table for explainability, but it is a record, not the input to rebuilds.

## Consequences

- Storage grows with message volume, not just fact volume. Mitigation: a configurable retention policy for episodes that have already been processed (off by default, because it disables rebuilds for those episodes).
- Rebuilds with a different model may produce different facts. This is intended, and `rebuild(dry_run=True)` will report the diff before applying it.
- The hot buffer (unprocessed episodes shown in context) comes for free, because unprocessed episodes are already stored.
- Raw episodes are also searchable, which lets the context builder answer detail questions that no extracted fact covers.

## Revisit when

- Episode storage becomes a measurable cost problem for typical users.
- A rebuild of a realistic scope (10k episodes) takes longer than a few minutes even with a warm cache.
