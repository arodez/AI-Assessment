const express = require('express');
const db = require('../db');
const requireOrganizer = require('../middleware/requireOrganizer');

const router = express.Router();

router.post('/organizer/login', (req, res) => {
  const { password } = req.body || {};
  if (typeof password !== 'string' || password !== process.env.ORGANIZER_PASSWORD) {
    return res.status(401).json({ error: 'invalid_password', message: 'Incorrect password.' });
  }
  req.session.organizer = true;
  res.json({ message: 'Logged in.' });
});

router.post('/organizer/logout', (req, res) => {
  req.session = null;
  res.json({ message: 'Logged out.' });
});

router.get('/organizer/session', (req, res) => {
  res.json({ loggedIn: !!(req.session && req.session.organizer) });
});

router.get('/organizer/events', requireOrganizer, (req, res) => {
  const rows = db
    .prepare(
      `SELECT e.*, COUNT(a.id) AS signup_count
       FROM events e
       LEFT JOIN attendees a ON a.event_id = e.id
       GROUP BY e.id
       ORDER BY e.event_date ASC`
    )
    .all();

  res.json(
    rows.map((row) => ({
      id: row.id,
      title: row.title,
      description: row.description,
      event_date: row.event_date,
      capacity: row.capacity,
      signupCount: row.signup_count,
    }))
  );
});

router.get('/organizer/events/:id/attendees', requireOrganizer, (req, res) => {
  const eventId = Number(req.params.id);
  const event = db.prepare('SELECT * FROM events WHERE id = ?').get(eventId);
  if (!event) {
    return res.status(404).json({ error: 'not_found', message: 'Event not found.' });
  }

  const attendees = db
    .prepare('SELECT name, email, created_at FROM attendees WHERE event_id = ? ORDER BY created_at ASC')
    .all(eventId);

  res.json({ event: { id: event.id, title: event.title }, attendees });
});

router.get('/organizer/events/:id/attendees/export.csv', requireOrganizer, (req, res) => {
  const eventId = Number(req.params.id);
  const event = db.prepare('SELECT * FROM events WHERE id = ?').get(eventId);
  if (!event) {
    return res.status(404).json({ error: 'not_found', message: 'Event not found.' });
  }

  const attendees = db
    .prepare('SELECT name, email, created_at FROM attendees WHERE event_id = ? ORDER BY created_at ASC')
    .all(eventId);

  const csvEscape = (value) => `"${String(value).replace(/"/g, '""')}"`;
  const lines = ['name,email,signed_up_at'];
  for (const a of attendees) {
    lines.push([csvEscape(a.name), csvEscape(a.email), csvEscape(a.created_at)].join(','));
  }

  const filename = `attendees-event-${eventId}.csv`;
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
  res.send(lines.join('\n'));
});

module.exports = router;
