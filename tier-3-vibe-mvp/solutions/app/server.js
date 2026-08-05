'use strict';

const http = require('node:http');
const { URL } = require('node:url');

const { loadEnv } = require('./loadEnv');
loadEnv();

const db = require('./db');
const { validateEventInput, validateRsvpInput } = require('./validation');
const { eventsListPage } = require('./views/eventsList');
const { eventDetailPage } = require('./views/eventDetail');
const { eventCreatePage } = require('./views/eventCreate');
const { organizerLoginPage } = require('./views/organizerLogin');
const { organizerDashboardPage } = require('./views/organizerDashboard');
const { organizerEventAttendeesPage } = require('./views/organizerEventAttendees');
const { escapeHtml } = require('./views/escape');
const { layout } = require('./views/layout');

const PORT = process.env.PORT || 3000;

// Fallback default is a clearly-labeled placeholder for local dev only.
// Documented in SECURITY_CHECK.md and README.md as an MVP limitation:
// real deployments MUST set ORGANIZER_TOKEN via environment / .env.
const ORGANIZER_TOKEN = process.env.ORGANIZER_TOKEN || 'dev-only-change-me';

function send(res, status, body, headers = {}) {
  res.writeHead(status, { 'Content-Type': 'text/html; charset=utf-8', ...headers });
  res.end(body);
}

function sendCsv(res, filename, csvText) {
  res.writeHead(200, {
    'Content-Type': 'text/csv; charset=utf-8',
    'Content-Disposition': `attachment; filename="${filename}"`,
  });
  res.end(csvText);
}

function notFound(res) {
  send(res, 404, layout({
    title: 'Not Found',
    body: `<div class="alert error">Page not found.</div><a class="btn-link" href="/">← Back home</a>`,
  }));
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    let size = 0;
    const MAX_SIZE = 1_000_000; // 1MB cap against abusive payloads
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_SIZE) {
        reject(new Error('Payload too large'));
        req.destroy();
        return;
      }
      data += chunk;
    });
    req.on('end', () => {
      try {
        const params = new URLSearchParams(data);
        const obj = {};
        for (const [k, v] of params.entries()) obj[k] = v;
        resolve(obj);
      } catch (err) {
        reject(err);
      }
    });
    req.on('error', reject);
  });
}

function isOrganizerAuthed(url, req) {
  // Token can come from query string (for simple links) — this is an MVP
  // simplification, documented as a limitation (token visible in URLs/logs).
  const token = url.searchParams.get('token');
  return typeof token === 'string' && token.length > 0 && token === ORGANIZER_TOKEN;
}

function csvEscapeField(value) {
  const str = String(value ?? '');
  if (/[",\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function attendeesToCsv(attendees) {
  const header = ['name', 'email', 'signed_up_at'];
  const lines = [header.join(',')];
  for (const a of attendees) {
    lines.push([csvEscapeField(a.name), csvEscapeField(a.email), csvEscapeField(a.created_at)].join(','));
  }
  return lines.join('\n') + '\n';
}

const server = http.createServer(async (req, res) => {
  let url;
  try {
    url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  } catch (_) {
    return notFound(res);
  }

  const { pathname } = url;
  const method = req.method;

  try {
    // ---------- Public: list upcoming events ----------
    if (method === 'GET' && pathname === '/') {
      const events = db.listUpcomingEventsWithSpots();
      return send(res, 200, eventsListPage({ events }));
    }

    // ---------- Public: create event form ----------
    if (method === 'GET' && pathname === '/events/new') {
      return send(res, 200, eventCreatePage({ errors: null, values: null }));
    }

    // ---------- Public: create event submit ----------
    if (method === 'POST' && pathname === '/events') {
      const body = await parseBody(req);
      const result = validateEventInput({
        title: body.title,
        eventDate: body.eventDate,
        description: body.description,
        capacity: body.capacity,
      });

      if (!result.valid) {
        return send(res, 400, eventCreatePage({ errors: result.errors, values: body }));
      }

      const event = db.createEvent(result.data);
      res.writeHead(302, { Location: `/events/${event.id}` });
      return res.end();
    }

    // ---------- Public: single event detail + RSVP form ----------
    const eventDetailMatch = pathname.match(/^\/events\/(\d+)$/);
    if (method === 'GET' && eventDetailMatch) {
      const eventId = Number(eventDetailMatch[1]);
      const events = db.listAllEventsWithSpots();
      const event = events.find((e) => e.id === eventId);
      if (!event) return notFound(res);
      const success = url.searchParams.get('success') === '1';
      return send(res, 200, eventDetailPage({ event, errors: null, success }));
    }

    // ---------- Public: RSVP submit ----------
    const rsvpMatch = pathname.match(/^\/events\/(\d+)\/rsvp$/);
    if (method === 'POST' && rsvpMatch) {
      const eventId = Number(rsvpMatch[1]);
      const body = await parseBody(req);

      const events = db.listAllEventsWithSpots();
      const event = events.find((e) => e.id === eventId);
      if (!event) return notFound(res);

      const validation = validateRsvpInput({ name: body.name, email: body.email });
      if (!validation.valid) {
        return send(res, 400, eventDetailPage({ event, errors: validation.errors, success: false }));
      }

      const result = db.signUpForEvent({
        eventId,
        name: validation.data.name,
        email: validation.data.email,
      });

      if (!result.ok) {
        const freshEvents = db.listAllEventsWithSpots();
        const freshEvent = freshEvents.find((e) => e.id === eventId);
        let errors;
        if (result.reason === 'full') {
          errors = ['This event is already full.'];
        } else if (result.reason === 'duplicate') {
          errors = ['This email has already signed up for this event.'];
        } else {
          errors = ['Could not complete sign-up.'];
        }
        return send(res, 409, eventDetailPage({ event: freshEvent, errors, success: false }));
      }

      res.writeHead(302, { Location: `/events/${eventId}?success=1` });
      return res.end();
    }

    // ---------- Organizer: login ----------
    if (method === 'GET' && pathname === '/organizer') {
      if (isOrganizerAuthed(url, req)) {
        const events = db.listAllEventsWithSpots();
        return send(res, 200, organizerDashboardPage({ events, token: url.searchParams.get('token') }));
      }
      return send(res, 200, organizerLoginPage({ error: null }));
    }

    if (method === 'POST' && pathname === '/organizer') {
      const body = await parseBody(req);
      if (body.token === ORGANIZER_TOKEN) {
        res.writeHead(302, { Location: `/organizer?token=${encodeURIComponent(body.token)}` });
        return res.end();
      }
      return send(res, 401, organizerLoginPage({ error: 'Invalid token.' }));
    }

    // ---------- Organizer: single event attendee list ----------
    const orgEventMatch = pathname.match(/^\/organizer\/events\/(\d+)$/);
    if (method === 'GET' && orgEventMatch) {
      if (!isOrganizerAuthed(url, req)) {
        return send(res, 401, organizerLoginPage({ error: 'Invalid or missing token.' }));
      }
      const eventId = Number(orgEventMatch[1]);
      const event = db.getEventById(eventId);
      if (!event) return notFound(res);
      const attendees = db.listAttendeesForEvent(eventId);
      return send(res, 200, organizerEventAttendeesPage({
        event, attendees, token: url.searchParams.get('token'),
      }));
    }

    // ---------- Organizer: CSV export ----------
    const csvMatch = pathname.match(/^\/organizer\/events\/(\d+)\/export\.csv$/);
    if (method === 'GET' && csvMatch) {
      if (!isOrganizerAuthed(url, req)) {
        return send(res, 401, organizerLoginPage({ error: 'Invalid or missing token.' }));
      }
      const eventId = Number(csvMatch[1]);
      const event = db.getEventById(eventId);
      if (!event) return notFound(res);
      const attendees = db.listAttendeesForEvent(eventId);
      const csv = attendeesToCsv(attendees);
      const safeFilename = `attendees-event-${eventId}.csv`;
      return sendCsv(res, safeFilename, csv);
    }

    return notFound(res);
  } catch (err) {
    console.error('Unhandled error:', err);
    return send(res, 500, layout({
      title: 'Error',
      body: `<div class="alert error">Something went wrong. Please try again.</div>`,
    }));
  }
});

server.listen(PORT, () => {
  console.log(`Community Events Hub running at http://localhost:${PORT}`);
  if (!process.env.ORGANIZER_TOKEN) {
    console.log(`[WARN] ORGANIZER_TOKEN not set — using insecure dev default. Set it in .env for real use.`);
  }
});
