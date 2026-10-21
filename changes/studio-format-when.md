# What

- Add `formatWhen(value: string | null): string` in `studio/lib/format-when.ts`: `YYYY-MM-DD HH:MM:SS`, with `—` for null or empty values.
- Map's fact table (`valid_from`, `recorded_at`) uses it through the new helper instead of the local `when()`, which is removed.
- Ops' recent-request times use it instead of the inline `String(row.at ?? "—").replace("T", " ").slice(0, 19)`.

# Why

The same ISO timestamps were formatted with two local implementations that could drift: Map's helper kept a `+05:30` offset where Ops' cap cut it, and Ops rendered an empty `at` as a blank cell where Map showed `—` (#45). One shared helper gives both screens the same shape.
