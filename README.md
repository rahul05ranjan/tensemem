# TenseMem

**Memory that knows its tenses.** An embedded, deterministic state memory engine for AI agents.

> Status: pre-alpha. The engine is under active development; this release only reserves the package name.

## The problem

Vector memory has no idea what is current. Tell an agent "I live in Delhi" in January and "I moved to Bangalore" in June, and a similarity search returns both, leaving the model to guess.

## What TenseMem does

- Turns conversations into structured, versioned facts.
- When a fact changes, the old value is superseded rather than deleted: the agent sees only what is true *now*, and the full history stays available for "where did I live before?"
- Runs as a single SQLite file inside your process. No graph database, no vector cluster, no server.
- The LLM proposes facts; deterministic, tested rules decide how they change state.
- Every fact can explain where it came from and what it replaced.

## Planned API

```python
from tensemem import Memory

mem = Memory()
mem.add("I moved to Bangalore last week and now only write Rust.", user_id="u1")
print(mem.context(user_id="u1", max_tokens=200).text)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and workflow, and [docs/adr](docs/adr) for the design decisions behind the engine.

## License

[Apache-2.0](LICENSE)
