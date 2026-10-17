# 0005. Facts track both valid time and recorded time

- Status: Accepted
- Date: 2026-10-17

## Context

There are two different questions about time:

1. **When was this true in the world?** "I moved to Bangalore last week" means the new city has been true since about a week before the message, not since the moment we processed it.
2. **When did the system know it?** This matters for debugging ("why did the agent say Delhi yesterday?") and for auditing.

A single `created_at` column, as in the PDF's MVP, conflates the two. It also makes processing order decide the outcome, so a late-arriving or backfilled older message can overwrite newer information.

## Decision

1. Every fact has **valid time**: `valid_from`, `valid_to`, and `valid_precision` (`instant`, `day`, `month`, `year`, `unknown`).
2. Every fact has **recorded time**: `recorded_at` (when we stored it) and `invalidated_at` (when we stopped believing it).
3. **Valid time decides ordering.** A new value supersedes the active one only if its `valid_from` is the same or later. An older value arriving late is inserted into history in the right position and does not displace the current value. This makes the final state independent of processing order.
4. **Relative dates are resolved against the episode's `occurred_at`**, not the processing time. Developers importing old chat logs pass the original timestamps.
5. When the text gives no date, `valid_from` is the episode's `occurred_at` and `valid_precision` is `unknown`.
6. **Storage format:** all timestamps are UTC, stored as fixed-width ISO 8601 text (`YYYY-MM-DDTHH:MM:SS.ffffffZ`). Fixed width means text comparison equals time comparison, so SQLite indexes work correctly for range queries. Day, month and year precision values are stored as the start of that period, and the precision field controls how they are displayed and compared.
7. **Comparisons respect precision.** Two values whose periods overlap (for example "October 2026" and "2026-10-10") are treated as concurrent, and ties fall back to recorded time.
8. All code reads time through a **clock abstraction**, so tests can control time precisely.

## Alternatives considered

- **Single timestamp (processing time).** Simple, but out-of-order processing corrupts state and "since when" questions can't be answered.
- **Valid time only.** Answers questions about the world, but loses the audit trail of what the system believed and when.
- **Native datetime types.** SQLite has none; storing epoch integers is viable but harder to read and debug, and loses the precision information.

## Consequences

- Questions such as "where did I live in March?" and "what did we believe last Tuesday?" become simple range queries.
- Out-of-order and parallel processing is safe, which the job queue relies on.
- The extractor must output dates with a precision, and the temporal resolver needs a rule-based fallback for common phrases. Wrong dates are a new class of extraction error to measure in the golden set.
- The context renderer can say "since ~Oct 2026; previously Delhi", which helps the model answer questions about the past.

## Revisit when

- Precision-aware comparison rules produce confusing results in real usage (for example many ties at month precision).
- A backend with native temporal types (Postgres `tstzrange`) is added, at which point that backend should use them while keeping the same API.
