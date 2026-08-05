'use strict';

const { escapeHtml } = require('./escape');
const { layout } = require('./layout');

function organizerLoginPage({ error }) {
  const alert = error ? `<div class="alert error">${escapeHtml(error)}</div>` : '';
  const body = `
    <div class="card">
      <h2>Organizer Access</h2>
      <p class="meta">Enter the organizer token to view attendee lists.</p>
      ${alert}
      <form method="POST" action="/organizer">
        <label for="token">Organizer token</label>
        <input type="password" id="token" name="token" required autofocus>
        <button type="submit">Enter</button>
      </form>
    </div>
  `;
  return layout({ title: 'Organizer Access', body, activeNav: 'organizer' });
}

module.exports = { organizerLoginPage };
