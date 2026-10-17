# 0008. Corrections are first-class and survive rebuilds

- Status: Accepted
- Date: 2026-10-17

## Context

Extraction will sometimes be wrong. A misread sentence can create "lives in Pune" and, worse, supersede the correct "lives in Bangalore". Users and developers need a reliable way to say "that fact is wrong".

Deleting the fact is not enough:

- **Rebuilds bring it back.** Facts are a projection of episodes (ADR 0001). Replaying the same episode can re-extract the same wrong fact, and the rebuilt fact has a new ID.
- **The damage isn't undone.** If the wrong fact superseded a correct one, deleting it leaves the slot empty instead of restoring the correct value.
- **"Wrong" is different from "no longer true".** `RETRACT` means a fact *was* true until some point. A correction means it was *never* true, so it must not appear in history either.

## Decision

1. **`correct(fact_id, replacement=None, note=None)`** marks a fact `REJECTED`. Rejected facts are excluded from current state and from history.
2. **Corrections are stored as episodes** of kind `explicit_op` (per ADR 0001), so they are part of the log and replayed by `rebuild()`.
3. **A correction is stored as a rejected claim, not a fact ID**: `(scope, subject, predicate, object_norm)` plus the sequence number of the correction. During extraction and rebuilds, the resolver drops any operation matching a rejected claim that comes from an episode at or before that sequence number. Episodes *after* the correction can assert the claim again, because the user may genuinely move to Pune later.
4. **The affected slot is re-resolved.** After rejecting a fact, the resolver recomputes the slot from its remaining facts. A value that was superseded only by the rejected fact becomes `ACTIVE` again. This reuses the normal resolver logic rather than special undo code.
5. **`replacement`** optionally applies a correct value in the same transaction (equivalent to `set()` with the correction as evidence).
6. **Corrections from conversation** use a new extractor operation, `DENY`, for statements such as "I never lived in Pune" or "that's wrong, I'm not vegetarian". `DENY` targets an existing fact and is applied exactly like `correct()`. It requires user-authored evidence (ADR 0007).
7. **Corrections are attributed.** Every fact records the extractor version (model and prompt version) that produced it, and `stats()` reports corrections per extractor version, so prompt or model regressions show up as data.

## Alternatives considered

- **Delete the fact.** Re-extracted on rebuild; doesn't restore the superseded value.
- **Reuse `RETRACT`.** Puts a never-true value into history ("previously lived in Pune"), which is misinformation.
- **Store corrections by fact ID.** IDs change on rebuild, so the correction would be lost.
- **Block the claim forever.** Prevents a legitimate later change from being recorded.

## Consequences

- `REJECTED` becomes a real lifecycle state with two entry points: `correct()` and `DENY`.
- The resolver needs a "recompute slot" operation. It is also useful for `forget()` of a single fact and for repairs after migrations.
- Rebuilds are correction-aware, so upgrading the extractor never reintroduces errors a user already fixed.
- Per-extractor correction counts provide a feedback signal for improving prompts and choosing models.

## Revisit when

- Users need to correct a fact for one consumer but not another (per-agent views of the same memory).
- Correction volume suggests a review queue for low-confidence facts would be cheaper than after-the-fact fixes.
