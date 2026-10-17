# 0002. The LLM proposes typed operations; deterministic code applies them

- Status: Accepted
- Date: 2026-10-17

## Context

Someone has to decide what happens to existing memory when a new statement arrives. "I moved to Bangalore" should replace the old city. "I also write Go" should add a language. "I might move to Pune" should change nothing.

Existing tools put that decision in the LLM: some ask the model to choose ADD/UPDATE/DELETE for each new fact, and others ask the agent to call memory-editing tools. Both make correctness depend on the model's judgment on every turn, which varies between models, prompt versions and even runs. Small and local models are noticeably worse at it.

## Decision

Split the work in two:

1. **The LLM extracts.** It reads the messages and returns a list of typed operations validated against a schema: subject, predicate, object, operation (`SET`, `ADD`, `REMOVE`, `RETRACT`, `REPLACE_SET`), modality (asserted, planned, hypothetical, negated), confidence, valid-from date, and an exact evidence quote. It is told the existing predicates and the current facts for the scope so it reuses canonical names.
2. **The engine decides.** A pure function `resolve(snapshot, ops) -> mutations` applies a fixed decision table: supersede, reinforce, insert as history, retract, store as candidate, or drop. It knows predicate cardinality, ordering by valid time, and confidence thresholds. A separate `apply(mutations)` step writes the result in one transaction.
3. **Hard invariants live in the database.** "At most one active fact per slot" is a partial unique index, so a bug in the resolver fails loudly instead of corrupting state.
4. **The LLM may help with narrow, recorded judgments**, such as whether "editor" and "preferred_ide" are the same predicate. Those answers are cached and stored as alias records, so they are reviewable and replayable. The LLM never directly changes a fact's status.
5. **Every transition is logged** in `fact_events` with a machine-readable reason, which powers `explain()`.

## Alternatives considered

- **LLM decides updates.** Fewer moving parts, handles unusual cases flexibly, but correctness is probabilistic and hard to test. A model upgrade can silently change behavior.
- **Agent edits its own memory through tool calls.** Maximally flexible, but depends on the agent remembering to call tools, costs tokens on the main turn, and small models corrupt state.
- **No LLM at all (rules or NER only).** Fully deterministic but far too weak at understanding natural language.

## Consequences

- We need a **predicate registry with cardinality** (ONE vs MANY), shipped with a starter ontology of common predicates and extensible at runtime. This is real work, and it is also the main thing that makes TenseMem better than competitors at state changes.
- Extraction mistakes still happen, but they are **bounded**: a wrong extraction can produce a wrong fact, but it can't break invariants, and the evidence link makes it easy to find and fix.
- The resolver can be **exhaustively unit tested and property tested** without any LLM.
- The deterministic API (`set()`, `add_value()`, …) uses the same resolver, so developers can bypass the LLM entirely and get identical semantics.
- Unusual statements the decision table doesn't cover are dropped or stored as candidates rather than guessed at. We prefer missing a fact over corrupting state.

## Revisit when

- Golden-set analysis shows a recurring class of statements that the decision table handles wrongly and that can't be fixed by adding an operation or a rule.
