# 0004. Embeddings are optional; full-text search is the default retrieval path

- Status: Accepted
- Date: 2026-10-17

## Context

Most memory libraries require a vector index. That brings heavy dependencies (embedding models, `numpy`, native extensions such as `sqlite-vec`), ties stored data to one embedding model and dimension, and adds a network call or model load to every query.

TenseMem's main retrieval problem is different from document RAG. A single user typically has hundreds to a few thousand facts, many of which are found by predicate (`lives_in`, `employer`) rather than by meaning. A pinned core profile plus keyword search covers most queries.

Native SQLite extensions are also unreliable to load: some Python builds (including macOS system Python and some pyenv builds) disable `enable_load_extension`.

## Decision

1. **The default install has no embeddings.** Retrieval uses the pinned core profile, predicate matching, recency, and SQLite's built-in **FTS5** full-text search with BM25 ranking.
2. **Embeddings are an opt-in extra:** `tensemem[local]` (a small local ONNX model via `fastembed`) or an API embedder (`tensemem[openai]`). One config flag enables them.
3. **Embeddings are stored as plain BLOBs keyed by `(owner, model)`.** Switching models doesn't need a schema change, and several models can coexist during a migration.
4. **Vector search is brute force within a scope**, using `numpy`. With a few thousand vectors per user this takes about a millisecond and needs no native extension. `sqlite-vec` may be added later as an accelerator, only if benchmarks show a need.
5. **Embeddings are computed by a background job**, never inside a write transaction. Facts are searchable by FTS immediately and by vector once the job finishes.
6. **Benchmarks report both configurations**, with and without embeddings, so users can make an informed choice.

## Alternatives considered

- **Embeddings by default with `sqlite-vec`** (the PDF's plan). Better semantic recall out of the box, but heavier installs, extension-loading failures, and a fixed vector dimension in the schema.
- **Embeddings by default through the user's LLM provider API.** No local model, but a network call on every query and a hard dependency on that provider.
- **A separate vector database.** Contradicts the zero-infrastructure positioning.

## Consequences

- The core install stays tiny (`pydantic`, `httpx`) and works on every platform.
- Paraphrased queries with no keyword overlap ("where's home for me?") rely on predicate descriptions and the core profile rather than vectors. This is the main quality risk of this decision and must be measured.
- Read latency without embeddings stays in the low single-digit milliseconds, because the read path makes no network or model calls.

## Revisit when

- TenseBench shows that enabling local embeddings improves answer accuracy by more than about 5 percentage points on typical scenarios. At that point we should make `tensemem[local]` the recommended default in the quickstart.
- Per-scope fact counts in real usage regularly exceed about 50k, where brute-force search stops being cheap.
