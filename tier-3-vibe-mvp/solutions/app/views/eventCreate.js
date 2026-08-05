'use strict';

const { escapeHtml } = require('./escape');
const { layout } = require('./layout');

function eventCreatePage({ errors, values }) {
  const v = values || {};
  const alert = errors && errors.length
    ? `<div class="alert error">${errors.map(escapeHtml).join('<br>')}</div>`
    : '';

  const body = `
    <div class="card">
      <h2>Create Event</h2>
      ${alert}
      <form method="POST" action="/events">
        <label for="title">Title</label>
        <input type="text" id="title" name="title" required maxlength="200" value="${escapeHtml(v.title || '')}">

        <label for="eventDate">Date</label>
        <input type="date" id="eventDate" name="eventDate" required value="${escapeHtml(v.eventDate || '')}">

        <label for="description">Description (optional)</label>
        <textarea id="description" name="description" rows="4" maxlength="2000">${escapeHtml(v.description || '')}</textarea>

        <label for="capacity">Maximum capacity</label>
        <input type="number" id="capacity" name="capacity" required min="1" step="1" value="${escapeHtml(v.capacity || '')}">

        <button type="submit">Create Event</button>
      </form>
    </div>
  `;

  return layout({ title: 'Create Event', body, activeNav: 'create' });
}

module.exports = { eventCreatePage };
