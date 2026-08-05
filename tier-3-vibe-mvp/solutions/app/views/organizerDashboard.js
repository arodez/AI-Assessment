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

function organizerDashboardPage({ events, token }) {
  const rows = events.length
    ? events
        .map(
          (e) => `
        <tr>
          <td>${escapeHtml(e.title)}</td>
          <td>${escapeHtml(formatDate(e.event_date))}</td>
          <td>${e.signup_count}/${e.capacity}</td>
          <td><a href="/organizer/events/${e.id}?token=${encodeURIComponent(token)}" style="color:var(--accent);">View attendees</a></td>
        </tr>`
        )
        .join('\n')
    : '';

  const body = `
    <div class="card">
      <h2>Organizer Dashboard</h2>
      ${
        events.length
          ? `<table>
        <thead><tr><th>Event</th><th>Date</th><th>Signups</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`
          : `<div class="empty">No events yet.</div>`
      }
    </div>
  `;

  return layout({ title: 'Organizer Dashboard', body, activeNav: 'organizer' });
}

module.exports = { organizerDashboardPage };
