const loginSection = document.getElementById('login-section');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('login-form');
const loginMessage = document.getElementById('login-message');
const createForm = document.getElementById('create-form');
const createMessage = document.getElementById('create-message');
const eventsList = document.getElementById('events-list');

async function checkSession() {
  const res = await fetch('/api/organizer/session');
  const body = await res.json();
  if (body.loggedIn) {
    loginSection.style.display = 'none';
    dashboard.style.display = 'block';
    loadEvents();
  } else {
    loginSection.style.display = 'block';
    dashboard.style.display = 'none';
  }
}

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const password = document.getElementById('password').value;
  const res = await fetch('/api/organizer/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
  const body = await res.json();
  if (res.ok) {
    loginMessage.textContent = '';
    checkSession();
  } else {
    loginMessage.classList.add('error');
    loginMessage.textContent = body.message || 'Login failed.';
  }
});

document.getElementById('logout-btn').addEventListener('click', async () => {
  await fetch('/api/organizer/logout', { method: 'POST' });
  checkSession();
});

async function submitEvent(payload) {
  const res = await fetch('/api/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const body = await res.json();
  return { ok: res.ok, status: res.status, body };
}

createForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  createMessage.textContent = '';
  createMessage.className = 'message';

  const payload = {
    title: document.getElementById('title').value,
    description: document.getElementById('description').value,
    event_date: document.getElementById('event_date').value
      ? new Date(document.getElementById('event_date').value).toISOString()
      : '',
    capacity: Number(document.getElementById('capacity').value),
  };

  let result = await submitEvent(payload);

  if (!result.ok && result.status === 409 && result.body.error === 'overlap') {
    const names = result.body.conflictingEvents.map((ev) => ev.title).join(', ');
    const confirmed = window.confirm(
      `${result.body.message}\nConflicting: ${names}\n\nCreate it anyway?`
    );
    if (confirmed) {
      result = await submitEvent({ ...payload, force: true });
    } else {
      createMessage.classList.add('error');
      createMessage.textContent = 'Event creation cancelled.';
      return;
    }
  }

  if (result.ok) {
    createMessage.classList.add('success');
    createMessage.textContent = 'Event created.';
    createForm.reset();
    loadEvents();
  } else {
    createMessage.classList.add('error');
    createMessage.textContent =
      (result.body.details && result.body.details.join(' ')) ||
      result.body.message ||
      'Could not create event.';
  }
});

async function loadEvents() {
  const res = await fetch('/api/organizer/events');
  if (res.status === 401) {
    checkSession();
    return;
  }
  const events = await res.json();
  eventsList.innerHTML = '';

  if (events.length === 0) {
    eventsList.textContent = 'No events yet.';
    return;
  }

  for (const event of events) {
    eventsList.appendChild(renderEventRow(event));
  }
}

function renderEventRow(event) {
  const card = document.createElement('div');
  card.className = 'card';

  const title = document.createElement('h3');
  title.textContent = event.title;

  const meta = document.createElement('p');
  meta.className = 'meta';
  meta.textContent = `${new Date(event.event_date).toLocaleString()} · ${event.signupCount}/${event.capacity} signed up`;

  const viewBtn = document.createElement('button');
  viewBtn.textContent = 'View attendees';
  const attendeesContainer = document.createElement('div');

  viewBtn.addEventListener('click', async () => {
    const res = await fetch(`/api/organizer/events/${event.id}/attendees`);
    const body = await res.json();
    attendeesContainer.innerHTML = '';
    attendeesContainer.appendChild(renderAttendeesTable(body.attendees, event.id));
  });

  card.appendChild(title);
  card.appendChild(meta);
  card.appendChild(viewBtn);
  card.appendChild(attendeesContainer);

  return card;
}

function renderAttendeesTable(attendees, eventId) {
  const wrapper = document.createElement('div');

  const exportLink = document.createElement('a');
  exportLink.href = `/api/organizer/events/${eventId}/attendees/export.csv`;
  exportLink.textContent = 'Export CSV';
  exportLink.style.display = 'inline-block';
  exportLink.style.marginTop = '0.5rem';
  wrapper.appendChild(exportLink);

  if (attendees.length === 0) {
    const p = document.createElement('p');
    p.textContent = 'No signups yet.';
    wrapper.appendChild(p);
    return wrapper;
  }

  const table = document.createElement('table');
  const thead = document.createElement('tr');
  ['Name', 'Email', 'Signed up at'].forEach((h) => {
    const th = document.createElement('th');
    th.textContent = h;
    thead.appendChild(th);
  });
  table.appendChild(thead);

  for (const a of attendees) {
    const row = document.createElement('tr');
    const nameCell = document.createElement('td');
    nameCell.textContent = a.name;
    const emailCell = document.createElement('td');
    emailCell.textContent = a.email;
    const dateCell = document.createElement('td');
    dateCell.textContent = new Date(a.created_at).toLocaleString();
    row.appendChild(nameCell);
    row.appendChild(emailCell);
    row.appendChild(dateCell);
    table.appendChild(row);
  }

  wrapper.appendChild(table);
  return wrapper;
}

checkSession();
