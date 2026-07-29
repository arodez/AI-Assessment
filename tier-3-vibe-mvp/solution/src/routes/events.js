const express = require('express');
const db = require('../db');
const requireOrganizer = require('../middleware/requireOrganizer');
const { validateEventInput } = require('../validation');

const router = express.Router();

// Events within this many milliseconds of each other are considered
// "overlapping." The MVP has no event-duration field, so this is a
// simplifying stand-in for a real start/end range.
const OVERLAP_WINDOW_MS = 2 * 60 * 60 * 1000;

function toPublicEvent(row) {
  const spotsRemaining = row.capacity - row.signup_count;
  return {
    id: row.id,
    title: row.title,
    description: row.description,
    event_date: row.event_date,
    capacity: row.capacity,
    spotsRemaining: spotsRemaining < 0 ? 0 : spotsRemaining,
  };
}

router.get('/events', (req, res) => {
  const rows = db
    .prepare(
      `SELECT e.*, COUNT(a.id) AS signup_count
       FROM events e
       LEFT JOIN attendees a ON a.event_id = e.id
       WHERE e.event_date >= strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
       GROUP BY e.id
       ORDER BY e.event_date ASC`
    )
    .all();

  res.json(rows.map(toPublicEvent));
});

router.post('/events', requireOrganizer, (req, res) => {
  const { title, description, event_date, capacity, force } = req.body || {};
  const { valid, errors, parsedDate, capacityNum } = validateEventInput({
    title,
    description,
    event_date,
    capacity,
  });

  if (!valid) {
    return res.status(400).json({ error: 'Invalid event input.', details: errors });
  }

  const cleanTitle = title.trim();
  const cleanDescription = (description || '').trim();
  const isoDate = parsedDate.toISOString();

  if (!force) {
    const windowStart = new Date(parsedDate.getTime() - OVERLAP_WINDOW_MS).toISOString();
    const windowEnd = new Date(parsedDate.getTime() + OVERLAP_WINDOW_MS).toISOString();
    const overlapping = db
      .prepare(
        `SELECT id, title, event_date FROM events
         WHERE event_date BETWEEN ? AND ?`
      )
      .all(windowStart, windowEnd);

    if (overlapping.length > 0) {
      return res.status(409).json({
        error: 'overlap',
        message: 'This event overlaps with an existing event. Create it anyway?',
        conflictingEvents: overlapping,
      });
    }
  }

  const result = db
    .prepare(
      `INSERT INTO events (title, description, event_date, capacity) VALUES (?, ?, ?, ?)`
    )
    .run(cleanTitle, cleanDescription, isoDate, capacityNum);

  const created = db.prepare('SELECT * FROM events WHERE id = ?').get(result.lastInsertRowid);
  res.status(201).json(toPublicEvent({ ...created, signup_count: 0 }));
});

module.exports = router;
