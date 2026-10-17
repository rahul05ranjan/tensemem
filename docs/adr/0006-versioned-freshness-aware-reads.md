# 0006. Every read reports how fresh it is

- Status: Accepted
- Date: 2026-10-17

## Context

Extraction runs in the background (ADR 0001), so there is always a window between a message arriving and its facts being applied. A user says "I moved to Bangalore" and asks a question on the next turn; the facts may not be updated yet.

Memory tools generally answer from whatever state they have, with no indication of whether that state is current. A stale answer looks exactly like a fresh one. For an agent that takes actions (booking travel, editing code, changing an order) that is a correctness bug, and the caller has no way to detect it.

The hot buffer (showing unprocessed messages in context) softens the problem but doesn't let the caller *check* anything.

## Decision

1. **Every episode gets a sequence number.** The `episodes` table uses `INTEGER PRIMARY KEY AUTOINCREMENT`, so sequence numbers increase monotonically and are never reused, even after `forget()` deletes rows.
2. **`add()` returns the sequence number** of the last episode it stored (`AddResult.seq`).
3. **Each scope keeps a watermark**, `applied_seq`: every episode in the scope with a sequence number at or below it has reached a terminal state (processed, skipped, or failed). Jobs within a scope are processed in sequence order (one in flight per scope), so the watermark is a simple prefix. It is updated in the same transaction that commits the episode's facts.
4. **Every read reports its freshness.** `context()`, `state()`, `history()` and `search()` return:
   - `as_of_seq`: the scope's watermark at read time.
   - `latest_seq`: the highest sequence number ingested for the scope.
   - `pending`: number of episodes not yet applied.
   - `failed`: number of episodes whose extraction failed and hasn't been retried or dismissed.
   - `is_current`: true only when `pending == 0` and `failed == 0`.
   - `projection_version`: increases each time `rebuild()` regenerates facts, so callers can tell that facts were re-derived.
5. **Reads are snapshot-consistent.** Each read runs in a single read transaction (a WAL snapshot), so the reported `as_of_seq` describes exactly the facts returned.
6. **Callers can require freshness.** `context(min_seq=N, wait=seconds, on_stale=...)`:
   - If `as_of_seq >= N`, return normally.
   - Otherwise wait up to `wait` seconds for the scope to catch up (prioritizing that scope's jobs).
   - If it still hasn't caught up: with `on_stale="flag"` (default) return the result with `is_current=False` and the unprocessed messages in the hot buffer; with `on_stale="raise"` raise `StaleMemoryError`.
7. **Each fact records the sequence number of the episode that created it** (`recorded_seq`), so results can be compared with the watermark.
8. **Failures are visible, not silent.** A dead-lettered extraction keeps `is_current` false until it is retried successfully or explicitly dismissed (`tensemem jobs dismiss`). Dismissal is logged.

## Alternatives considered

- **Always block reads until extraction finishes.** Simple and always fresh, but puts LLM latency (often seconds) on every chat turn and fails hard when the provider is down.
- **Hot buffer only.** Helps the model but gives the caller nothing to check or enforce.
- **Timestamps instead of sequence numbers.** Clocks skew across processes and machines; a monotonic counter from the database is exact.
- **A global (database-wide) watermark.** One slow scope would make every other scope look stale. Per-scope watermarks match how memory is used.

## Consequences

- Callers can implement read-your-writes precisely: pass the `seq` from `add()` to the next `context()` call.
- Agents can choose their trade-off per call: answer immediately with a flag, wait briefly, or refuse to act on stale memory.
- Per-scope in-order processing becomes a hard requirement of the worker, not just an optimization.
- `rebuild()` must build into shadow tables and swap atomically, so readers never see a half-rebuilt projection; `projection_version` increments on swap.
- Monitoring gets a natural metric: the gap between `latest_seq` and `as_of_seq` per scope.

## Revisit when

- Per-scope in-order processing limits throughput for scopes with very high message volume.
- A distributed backend (Postgres, cloud) needs sequence numbers that are monotonic across writers; that backend may need a different watermark mechanism behind the same API.
