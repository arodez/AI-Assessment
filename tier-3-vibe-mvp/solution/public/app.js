async function loadEvents() {
  const container = document.getElementById('events');
  container.textContent = 'Loading…';

  const res = await fetch('/api/events');
  const events = await res.json();

  container.innerHTML = '';

  if (events.length === 0) {
    container.textContent = 'No upcoming events yet.';
    return;
  }

  for (const event of events) {
    container.appendChild(renderEventCard(event));
  }
}

function renderEventCard(event) {
  const card = document.createElement('div');
  card.className = 'card';

  const title = document.createElement('h3');
  title.textContent = event.title;

  const meta = document.createElement('p');
  meta.className = 'meta';
  meta.textContent = new Date(event.event_date).toLocaleString();

  const desc = document.createElement('p');
  desc.textContent = event.description || '';

  const spots = document.createElement('p');
  spots.className = 'spots' + (event.spotsRemaining <= 0 ? ' full' : '');
  spots.textContent =
    event.spotsRemaining <= 0
      ? 'Event is full'
      : `${event.spotsRemaining} spot(s) remaining of ${event.capacity}`;

  card.appendChild(title);
  card.appendChild(meta);
  card.appendChild(desc);
  card.appendChild(spots);

  if (event.spotsRemaining > 0) {
    card.appendChild(renderSignupForm(event.id));
  }

  return card;
}

function renderSignupForm(eventId) {
  const form = document.createElement('form');
  form.className = 'inline';

  const nameInput = document.createElement('input');
  nameInput.type = 'text';
  nameInput.placeholder = 'Your name';
  nameInput.required = true;

  const emailInput = document.createElement('input');
  emailInput.type = 'email';
  emailInput.placeholder = 'you@example.com';
  emailInput.required = true;

  const submit = document.createElement('button');
  submit.type = 'submit';
  submit.textContent = 'Sign up';

  const message = document.createElement('p');
  message.className = 'message';

  form.appendChild(nameInput);
  form.appendChild(emailInput);
  form.appendChild(submit);
  form.appendChild(message);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    message.textContent = '';
    message.className = 'message';

    const res = await fetch(`/api/events/${eventId}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: nameInput.value, email: emailInput.value }),
    });
    const body = await res.json();

    if (res.ok) {
      message.classList.add('success');
      message.textContent = body.message;
      form.reset();
      // Delay the list refresh so the success message is actually visible
      // instead of being wiped out by the re-render in the same tick.
      setTimeout(loadEvents, 1500);
    } else {
      message.classList.add('error');
      message.textContent = body.message || 'Something went wrong.';
    }
  });

  return form;
}

loadEvents();
