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

function eventsListPage({ events }) {
  const cards = events.length
    ? events
        .map((e) => {
          const spotsClass = e.spots_left <= 0 ? 'low' : e.spots_left <= 3 ? 'low' : 'ok';
          const spotsLabel =
            e.spots_left <= 0 ? 'Full' : `${e.spots_left} spot${e.spots_left === 1 ? '' : 's'} left`;
          return `
          <div class="card">
            <h2>${escapeHtml(e.title)}</h2>
            <div class="meta">${escapeHtml(formatDate(e.event_date))}</div>
            ${e.description ? `<p>${escapeHtml(e.description)}</p>` : ''}
            <div class="spots ${spotsClass}">${escapeHtml(spotsLabel)}</div>
            <a class="btn-link" href="/events/${e.id}">View & sign up →</a>
          </div>`;
        })
        .join('\n')
    : `<div class="empty">No upcoming events yet. <a href="/events/new" style="color:var(--accent);">Create one</a>.</div>`;

  const body = `
    <h2 style="font-weight:600;font-size:1.1rem;margin-bottom:1rem;">Upcoming Events</h2>
    ${cards}
  `;

  return layout({ title: 'Upcoming Events', body, activeNav: 'events' });
}

module.exports = { eventsListPage };
