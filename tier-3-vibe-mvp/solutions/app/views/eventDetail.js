'use strict';

const { escapeHtml } = require('./escape');
const { layout } = require('./layout');

function formatDate(iso) {
  try {
    return new Date(iso + 'T00:00:00').toLocaleDateString(undefined, {
      weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
    });
  } catch (_) {
    return iso;
  }
}

function eventDetailPage({ event, errors, success }) {
  const isFull = event.spots_left <= 0;

  const alert = errors && errors.length
    ? `<div class="alert error">${errors.map(escapeHtml).join('<br>')}</div>`
    : success
      ? `<div class="alert success">You're signed up! See you there.</div>`
      : '';

  const form = isFull
    ? `<div class="alert error">This event is full. No more spots available.</div>`
    : `
    <form method="POST" action="/events/${event.id}/rsvp">
      <label for="name">Your name</label>
      <input type="text" id="name" name="name" required maxlength="200">
      <label for="email">Your email</label>
      <input type="email" id="email" name="email" required>
      <button type="submit">Sign up</button>
    </form>`;

  const body = `
    <a class="btn-link" href="/" style="margin-bottom:1rem;">← Back to events</a>
    <div class="card">
      <h2>${escapeHtml(event.title)}</h2>
      <div class="meta">${escapeHtml(formatDate(event.event_date))}</div>
      ${event.description ? `<p>${escapeHtml(event.description)}</p>` : ''}
      <div class="spots ${isFull ? 'low' : 'ok'}">
        ${isFull ? 'Full' : `${event.spots_left} spot${event.spots_left === 1 ? '' : 's'} left`}
        (${event.signup_count}/${event.capacity} signed up)
      </div>
    </div>
    ${alert}
    <div class="card">
      <h2 style="font-size:1rem;">RSVP</h2>
      ${form}
    </div>
  `;

  return layout({ title: event.title, body, activeNav: 'events' });
}

module.exports = { eventDetailPage };
