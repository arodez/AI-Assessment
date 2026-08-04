import { getDb } from "@/lib/db";

// Simple email validation regex helper
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(request) {
  try {
    const body = await request.json();
    const { eventId, email } = body;

    if (!eventId) {
      return new Response(JSON.stringify({ error: "Event ID is required." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!email || !emailRegex.test(email)) {
      return new Response(JSON.stringify({ error: "A valid email address is required." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const cleanEmail = email.trim().toLowerCase();

    const db = await getDb();

    // Check if event exists and calculate capacity
    const event = await db.get(
      `SELECT e.*, (SELECT COUNT(*) FROM rsvps r WHERE r.event_id = e.id) as rsvp_count FROM events e WHERE e.id = ?`,
      [eventId]
    );

    if (!event) {
      return new Response(JSON.stringify({ error: "Event not found." }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Block duplicate email RSVP for the same event
    const existingRsvp = await db.get(
      `SELECT id FROM rsvps WHERE event_id = ? AND email = ?`,
      [eventId, cleanEmail]
    );

    if (existingRsvp) {
      return new Response(JSON.stringify({ error: "You have already RSVP'd for this event." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Prevent RSVPs once capacity is reached
    if (event.rsvp_count >= event.max_capacity) {
      return new Response(JSON.stringify({ error: "This event is already at full capacity." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Insert RSVP
    await db.run(
      `INSERT INTO rsvps (event_id, email) VALUES (?, ?)`,
      [eventId, cleanEmail]
    );

    return new Response(
      JSON.stringify({ message: "RSVP successful!" }),
      {
        status: 201,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("POST RSVP error:", error);
    return new Response(JSON.stringify({ error: "Internal server error." }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
