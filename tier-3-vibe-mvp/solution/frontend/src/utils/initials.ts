/** First letter of up to the first 2 whitespace-separated words, or the
 * first 2 characters of a single word — covers both "Alice" (header
 * greeting, first_name only) -> "AL" and "Priya Nair" (host/attendee full
 * names) -> "PN". */
export function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '';
  if (parts.length === 1) {
    return (parts[0] ?? '').slice(0, 2).toUpperCase();
  }
  return parts
    .slice(0, 2)
    .map((p) => (p[0] ?? '').toUpperCase())
    .join('');
}
