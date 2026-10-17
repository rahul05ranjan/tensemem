# 0007. Memory never learns from its own output

- Status: Accepted
- Date: 2026-10-17

## Context

Memory output goes into the model's prompt. The conversation that follows is then sent back to memory for extraction. That creates a feedback loop with three channels:

1. **Raw echo.** The application passes the whole message list back to `add()`, including the system prompt or a message that contains the injected memory block.
2. **Assistant restatement.** The assistant says "Since you live in Bangalore, …", and that sentence is ingested.
3. **User confirmation.** The assistant asks "Are you still in Bangalore?" and the user answers "yes".

Without a guard, the system re-learns its own output. In the best case it creates duplicate facts; in the worst case it treats every echo as fresh evidence, inflating confidence in facts nobody re-stated, including wrong ones. Large stores built this way are known to fill up with duplicated and self-generated entries. Our resolver already merges exact duplicates (ADR 0002), but merging alone would still count each echo as reinforcement.

## Decision

1. **Fence everything memory outputs.** `context()` wraps its rendered text in a marker that carries a per-database secret tag, for example `<tensemem-context tag="k3f9…">…</tensemem-context>`. Before extraction, fenced spans are removed from the input. The raw episode is still stored unchanged for audit and replay.
2. **Extract only from user-authored text by default.** System messages are never extracted. Assistant messages are passed to the extractor only as *context* for interpreting the user (for example, the question the user is answering); they can't be the evidence for a fact.
3. **Evidence must be verbatim.** Every extracted operation includes an exact evidence quote. The pipeline checks that the quote appears in a user-authored, unfenced span of the episode. Operations that fail the check are dropped and counted. This also catches extractor hallucinations.
4. **Confirmations reinforce, but weakly.** When the user's evidence is a bare confirmation ("yes", "still true") of a question the assistant asked, the operation may reinforce an existing fact with a reduced confidence weight. It can never create a new fact or supersede one on its own.
5. **Restatement is not reinforcement.** Confidence only increases from evidence that passes rules 1–4. Re-extracting a fact the system itself served adds nothing.
6. **Measure it.** The benchmark suite includes conversations where context is injected and echoed back, and reports duplicate facts and unearned confidence growth (contamination rate). The target is zero.

## Alternatives considered

- **Tell the extractor not to re-extract recalled memories.** A prompt instruction works most of the time and fails silently the rest; it doesn't scale to small or local models.
- **Ask developers to strip memory before calling `add()`.** Easy to forget, and every integration would reimplement it.
- **Deduplicate only.** Prevents duplicate rows but still inflates confidence and still lets self-generated content count as evidence.
- **Extract from assistant messages with lower trust.** Useful for some agent designs, so it remains an opt-in setting, but it is exactly the channel through which echoes enter, so it is off by default.

## Consequences

- Facts that only ever appear in assistant text are not learned by default. This is deliberate: the assistant is not a source of truth about the user.
- Short confirmations need the preceding assistant question, so the extractor receives a small window of conversation context.
- The secret tag must be stable for a database (stored in its metadata) so fences written by one process are recognized by another.
- Developers who render memory themselves (without `context()`) lose fencing. The docs must say so, and `state()` results will expose a helper to fence custom renderings.

## Revisit when

- Real usage shows legitimate facts are routinely lost because they appear only in assistant turns.
- A provider or framework adds native, structured separation of injected context, which would make text fencing unnecessary.
