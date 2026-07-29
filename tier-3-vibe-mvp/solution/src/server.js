require('dotenv').config();
const path = require('path');
const express = require('express');
const cookieSession = require('cookie-session');

const eventsRouter = require('./routes/events');
const signupRouter = require('./routes/signup');
const organizerRouter = require('./routes/organizer');

if (!process.env.ORGANIZER_PASSWORD) {
  console.error('ORGANIZER_PASSWORD is not set. Copy .env.example to .env and set it.');
  process.exit(1);
}
if (!process.env.SESSION_SECRET) {
  console.error('SESSION_SECRET is not set. Copy .env.example to .env and set it.');
  process.exit(1);
}

const app = express();

app.use(express.json());
app.use(
  cookieSession({
    name: 'organizer_session',
    secret: process.env.SESSION_SECRET,
    httpOnly: true,
    sameSite: 'strict',
    maxAge: 8 * 60 * 60 * 1000,
  })
);

// No CORS middleware: this API is served same-origin to its own frontend only,
// and is not intended to be called from other sites or external scripts.
app.use('/api', eventsRouter);
app.use('/api', signupRouter);
app.use('/api', organizerRouter);

app.use(express.static(path.join(__dirname, '..', 'public')));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Community Events Hub listening on http://localhost:${PORT}`);
});
