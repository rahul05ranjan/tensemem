# 0003. SQLite is the default store, with one writer per process

- Status: Accepted
- Date: 2026-10-17

## Context

The core promise is zero setup: `pip install tensemem` and memory works, with no database server. SQLite is the obvious embedded store: it ships with Python, is extremely well tested, and is fast for this workload (small reads per user, modest write volume).

SQLite allows many readers but only one writer at a time. Naive use from several threads or async tasks produces `database is locked` errors under load, which is the most common complaint about SQLite in web apps.

## Decision

1. **SQLite is the default backend**, behind a `StorageBackend` protocol so a Postgres backend can be added later and pass the same conformance tests.
2. **One writer per process.** A dedicated writer thread owns the only write connection. All mutations are submitted to it as units of work and executed in order. The sync API waits on a future; the async API awaits it. This removes lock contention inside a process entirely.
3. **Readers use a small pool of read-only connections.** In WAL mode readers never block the writer or each other.
4. **Connection settings:** `journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON`, `busy_timeout=5000`.
5. **Write transactions are short and use `BEGIN IMMEDIATE`.** Slow work (LLM calls, embeddings) always happens **outside** a transaction. The resolver re-reads affected rows inside the transaction before applying changes.
6. **Multiple processes** (for example several web workers) are supported through `busy_timeout` plus retry with jitter on `SQLITE_BUSY`. For heavy multi-process use we recommend running `tensemem serve` and connecting over HTTP.
7. **Minimum SQLite version 3.35** (for `RETURNING` and modern JSON support) with **FTS5 required**. Both are checked when a database is opened, with a clear error message if missing.
8. Schema changes go through numbered migrations, applied automatically on open after an online backup.

## Alternatives considered

- **A connection per call with retries.** Simple, but under concurrency it spends time in retry loops and still surfaces lock errors at high load.
- **`aiosqlite` only.** Fine for async apps, but it still needs serialization, and many users write sync code.
- **DuckDB.** Excellent for analytics, but its concurrency model and transactional write pattern are a worse fit for many small writes.
- **Postgres by default.** Robust, but it breaks the zero-setup promise. It will be an optional backend.
- **An embedded graph database.** The heavy dependency we explicitly position against.

## Consequences

- No `database is locked` errors within a process, by construction.
- Write throughput is bounded by one connection per database. This is far above what LLM-bound extraction produces (each extraction takes hundreds of milliseconds), so it is not a practical limit.
- Durability beyond one machine requires replication (the Litestream pattern), backups, or the server and cloud modes. This must be documented clearly.
- The writer thread must shut down cleanly (`close()`, context manager, `atexit`) and must surface its exceptions to callers rather than dying silently.

## Revisit when

- Benchmarks show the single writer is the bottleneck for a realistic workload.
- Multi-process deployments become the dominant usage pattern, which would make server mode or Postgres the better default for them.
