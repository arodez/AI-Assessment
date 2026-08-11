/** Event.image_url is normally a relative path (e.g. "/uploads/events/x.jpg")
 * — the Vite dev server and Flask are different origins/ports, so it must
 * be prefixed with the API base URL to actually load. The Create Event
 * form's live preview instead passes an already-absolute `blob:` object
 * URL for the not-yet-uploaded cover photo, which must pass through
 * unchanged rather than getting the API origin prepended onto it. */
export function resolveImageUrl(imageUrl: string | null): string | null {
  if (!imageUrl) return null;
  if (/^(https?:|blob:|data:)/.test(imageUrl)) return imageUrl;
  return `${import.meta.env.VITE_API_BASE_URL}${imageUrl}`;
}
