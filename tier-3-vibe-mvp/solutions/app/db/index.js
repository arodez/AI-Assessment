'use strict';

const { DatabaseSync } = require('node:sqlite');
const path = require('node:path');
const fs = require('node:fs');

const DB_PATH = path.join(__dirname, '..', 'data.sqlite');

// Ensure directory exists (it does, but defensive)
fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

const db = new DatabaseSync(DB_PATH);

db.exec(`
  CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    event_date TEXT NOT NULL,
    description TEXT,
    capacity INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS attendees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    email_normalized TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (event_id) REFERENCES events(id)
  );

  CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_signup
    ON attendees(event_id, email_normalized);
`);

// ---- Events ----

function createEvent({ title, eventDate, description, capacity }) {
  const stmt = db.prepare(
    `INSERT INTO events (title, event_date, description, capacity) VALUES (?, ?, ?, ?)`
  );
  const info = stmt.run(title, eventDate, description || '', capacity);
  return getEventById(Number(info.lastInsertRowid));
}

function getEventById(id) {
  const stmt = db.prepare(`SELECT * FROM events WHERE id = ?`);
  return stmt.get(id) || null;
}

function listUpcomingEventsWithSpots() {
  // "Upcoming" = event_date >= today (string comparison works for ISO YYYY-MM-DD)
  const todayIso = new Date().toISOString().slice(0, 10);
  const stmt = db.prepare(`
    SELECT
      e.id, e.title, e.event_date, e.description, e.capacity,
      (e.capacity - COALESCE(a.signup_count, 0)) AS spots_left,
      COALESCE(a.signup_count, 0) AS signup_count
    FROM events e
    LEFT JOIN (
      SELECT event_id, COUNT(*) AS signup_count
      FROM attendees
      GROUP BY event_id
    ) a ON a.event_id = e.id
    WHERE e.event_date >= ?
    ORDER BY e.event_date ASC
  `);
  return stmt.all(todayIso);
}

function listAllEventsWithSpots() {
  const stmt = db.prepare(`
    SELECT
      e.id, e.title, e.event_date, e.description, e.capacity,
      (e.capacity - COALESCE(a.signup_count, 0)) AS spots_left,
      COALESCE(a.signup_count, 0) AS signup_count
    FROM events e
    LEFT JOIN (
      SELECT event_id, COUNT(*) AS signup_count
      FROM attendees
      GROUP BY event_id
    ) a ON a.event_id = e.id
    ORDER BY e.event_date ASC
  `);
  return stmt.all();
}

// ---- Attendees / RSVP ----

/**
 * Attempts to sign up an attendee for an event.
 * Uses a transaction + the DB's UNIQUE index as the source of truth for
 * duplicate prevention (safe under concurrent requests, not just app-level
 * checks which can race).
 *
 * Returns: { ok: true, attendee } | { ok: false, reason: 'not_found' | 'full' | 'duplicate' }
 */
function signUpForEvent({ eventId, name, email }) {
  const emailNormalized = email.trim().toLowerCase();

  db.exec('BEGIN IMMEDIATE');
  try {
    const event = db.prepare(`SELECT * FROM events WHERE id = ?`).get(eventId);
    if (!event) {
      db.exec('ROLLBACK');
      return { ok: false, reason: 'not_found' };
    }

    const countRow = db
      .prepare(`SELECT COUNT(*) AS c FROM attendees WHERE event_id = ?`)
      .get(eventId);
    const currentCount = countRow.c;

    if (currentCount >= event.capacity) {
      db.exec('ROLLBACK');
      return { ok: false, reason: 'full' };
    }

    try {
      const stmt = db.prepare(
        `INSERT INTO attendees (event_id, name, email, email_normalized) VALUES (?, ?, ?, ?)`
      );
      const info = stmt.run(eventId, name.trim(), email.trim(), emailNormalized);
      db.exec('COMMIT');
      const attendee = db
        .prepare(`SELECT * FROM attendees WHERE id = ?`)
        .get(Number(info.lastInsertRowid));
      return { ok: true, attendee };
    } catch (err) {
      db.exec('ROLLBACK');
      // UNIQUE constraint violation -> duplicate email for this event
      if (String(err.message).includes('UNIQUE')) {
        return { ok: false, reason: 'duplicate' };
      }
      throw err;
    }
  } catch (err) {
    try { db.exec('ROLLBACK'); } catch (_) { /* already rolled back */ }
    throw err;
  }
}

function listAttendeesForEvent(eventId) {
  const stmt = db.prepare(
    `SELECT name, email, created_at FROM attendees WHERE event_id = ? ORDER BY created_at ASC`
  );
  return stmt.all(eventId);
}

module.exports = {
  createEvent,
  getEventById,
  listUpcomingEventsWithSpots,
  listAllEventsWithSpots,
  signUpForEvent,
  listAttendeesForEvent,
};
