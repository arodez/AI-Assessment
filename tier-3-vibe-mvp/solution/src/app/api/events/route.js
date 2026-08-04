import { getDb } from "@/lib/db";

// XSS Sanitization helper
function sanitizeString(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;");
}

export async function GET(request) {
  try {
    const db = await getDb();
    
    // Select events along with dynamic counts of RSVPs to compute remaining capacity
    const events = await db.all(`
      SELECT 
        e.*, 
        (SELECT COUNT(*) FROM rsvps r WHERE r.event_id = e.id) as rsvp_count
      FROM events e
      ORDER BY datetime(e.date) ASC
    `);

    return new Response(JSON.stringify(events), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("GET Events error:", error);
    return new Response(JSON.stringify({ error: "Failed to fetch events." }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}

export async function POST(request) {
  try {
    const body = await request.json();
    let { title, date, description, maxCapacity } = body;

    // 1. Validation: Title must be present and not empty
    if (!title || typeof title !== 'string' || title.trim() === '') {
      return new Response(JSON.stringify({ error: "Title is required and cannot be empty." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // 2. Validation: Date must be present and not in the past
    if (!date) {
      return new Response(JSON.stringify({ error: "Date is required." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const eventDate = new Date(date);
    const today = new Date();
    // Reset today time to midnight for simple day comparison
    today.setHours(0, 0, 0, 0);

    if (isNaN(eventDate.getTime())) {
      return new Response(JSON.stringify({ error: "Invalid date format." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (eventDate < today) {
      return new Response(JSON.stringify({ error: "Event date cannot be in the past." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // 3. Validation: Max Capacity must be a positive integer
    const capacityNum = parseInt(maxCapacity, 10);
    if (isNaN(capacityNum) || capacityNum <= 0) {
      return new Response(JSON.stringify({ error: "Max capacity must be a positive number greater than 0." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Sanitization to prevent XSS
    const cleanTitle = sanitizeString(title.trim());
    const cleanDescription = sanitizeString((description || '').trim());
    const cleanDate = date; // Format validated by Date constructor

    const db = await getDb();

    // New: Prevent duplicate event titles (case-insensitive)
    const existing = await db.get(`SELECT id FROM events WHERE LOWER(title) = LOWER(?)`, [cleanTitle]);
    if (existing) {
      return new Response(JSON.stringify({ error: "An event with this title already exists." }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const result = await db.run(
      `INSERT INTO events (title, date, description, max_capacity) VALUES (?, ?, ?, ?)`,
      [cleanTitle, cleanDate, cleanDescription, capacityNum]
    );

    return new Response(
      JSON.stringify({
        message: "Event created successfully.",
        event: {
          id: result.lastID,
          title: cleanTitle,
          date: cleanDate,
          description: cleanDescription,
          max_capacity: capacityNum,
        }
      }),
      {
        status: 201,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("POST Event error:", error);
    return new Response(JSON.stringify({ error: "Internal server error." }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
