import { getDb } from "@/lib/db";

export async function GET(request, { params }) {
  const { eventId } = await params;
  const db = await getDb();

  // Verify event exists
  const event = await db.get(`SELECT id FROM events WHERE id = ?`, [eventId]);
  if (!event) {
    return new Response(JSON.stringify({ error: "Event not found." }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Fetch attendee emails ordered by RSVP time
  const rows = await db.all(
    `SELECT email FROM rsvps WHERE event_id = ? ORDER BY created_at ASC`,
    [eventId]
  );
  const emails = rows.map(r => r.email);

  const url = new URL(request.url);
  if (url.searchParams.get("format") === "csv") {
    const csv = ["Email", ...emails].join("\n");
    return new Response(csv, {
      status: 200,
      headers: {
        "Content-Type": "text/csv",
        "Content-Disposition": `attachment; filename="event_${eventId}_attendees.csv"`,
      },
    });
  }

  return new Response(JSON.stringify({ emails }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}