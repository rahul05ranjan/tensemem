export function formatWhen(value: string | null): string {
  if (!value) {
    return "—";
  }
  return value.replace("T", " ").replace(/\.\d+.*/, "").replace("Z", "").slice(0, 19);
}
