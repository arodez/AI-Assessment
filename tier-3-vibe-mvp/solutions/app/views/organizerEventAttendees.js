'use strict';

const { escapeHtml } = require('./escape');
const { layout } = require('./layout');

function organizerEventAttendeesPage({ event, attendees, token }) {
  const rows = attendees.length
    ? attendees
        .map(
          (a) => `
        <tr>
          <td>${escapeHtml(a.name)}</td>
          <td>${escapeHtml(a.email)}</td>
          <td>${escapeHtml(a.created_at)}</td>
        </tr>`
        )
        .join('\n')
    : '';

  const body = `
    <a class="btn-link" href="/organizer?token=${encodeURIComponent(token)}" style="margin-bottom:1rem;">← Back to dashboard</a>
    <div class="card">
      <h2>${escapeHtml(event.title)} — Attendees</h2>
      <div class="meta">${attendees.length} / ${event.capacity} signed up</div>
      ${
        attendees.length
          ? `<table>
        <thead><tr><th>Name</th><th>Email</th><th>Signed up at</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <a class="btn-link" href="/organizer/events/${event.id}/export.csv?token=${encodeURIComponent(token)}">Export CSV →</a>`
          : `<div class="empty">No sign-ups yet.</div>`
      }
    </div>
  `;

  return layout({ title: `${event.title} — Attendees`, body, activeNav: 'organizer' });
}

module.exports = { organizerEventAttendeesPage };
