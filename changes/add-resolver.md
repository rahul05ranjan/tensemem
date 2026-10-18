## What

- Add `resolve(ops, snapshot) -> mutations`, a pure decision table (no SQLite, no LLM).
- Cover insert, reinforce, supersede, historical insert, candidate, retract, reject, drop, and REPLACE_SET.

## Why

The engine — not the model — must decide how memory changes, and those rules need to be unit-tested before we write facts.
