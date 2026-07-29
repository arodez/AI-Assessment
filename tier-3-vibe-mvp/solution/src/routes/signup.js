const express = require('express');
const db = require('../db');
const { validateSignupInput, normalizeEmail } = require('../validation');

const router = express.Router();

const signupTransaction = db.transaction((eventId, name, email) => {
  const event = db.prepare('SELECT * FROM events WHERE id = ?').get(eventId);
  if (!event) {
    return { status: 404, body: { error: 'not_found', message: 'Event not found.' } };
  }

  const signupCount = db
    .prepare('SELECT COUNT(*) AS count FROM attendees WHERE event_id = ?')
    .get(eventId).count;

  if (signupCount >= event.capacity) {
    return { status: 409, body: { error: 'full', message: 'This event is full.' } };
  }

  const existing = db
    .prepare('SELECT id FROM attendees WHERE event_id = ? AND email = ?')
    .get(eventId, email);

  if (existing) {
    return {
      status: 409,
      body: { error: 'duplicate', message: 'This email is already signed up for this event.' },
    };
  }

  try {
    db.prepare(
      'INSERT INTO attendees (event_id, name, email) VALUES (?, ?, ?)'
    ).run(eventId, name, email);
  } catch (err) {
    // UNIQUE(event_id, email) backstop in case of a concurrent duplicate insert.
    if (err.code === 'SQLITE_CONSTRAINT_UNIQUE') {
      return {
        status: 409,
        body: { error: 'duplicate', message: 'This email is already signed up for this event.' },
      };
    }
    throw err;
  }

  const spotsRemaining = event.capacity - (signupCount + 1);
  return { status: 201, body: { message: 'Signed up successfully.', spotsRemaining } };
});

router.post('/events/:id/signup', (req, res) => {
  const eventId = Number(req.params.id);
  if (!Number.isInteger(eventId)) {
    return res.status(400).json({ error: 'invalid_event', message: 'Invalid event id.' });
  }

  const { name, email } = req.body || {};
  const { valid, errors } = validateSignupInput({ name, email });
  if (!valid) {
    return res.status(400).json({ error: 'invalid_input', message: errors.join(' ') });
  }

  const cleanName = name.trim();
  const normalizedEmail = normalizeEmail(email);

  const result = signupTransaction(eventId, cleanName, normalizedEmail);
  res.status(result.status).json(result.body);
});

module.exports = router;
