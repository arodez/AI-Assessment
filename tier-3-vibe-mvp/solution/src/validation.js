const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isValidEmail(email) {
  return typeof email === 'string' && email.trim().length <= 254 && EMAIL_RE.test(email.trim());
}

function normalizeEmail(email) {
  return email.trim().toLowerCase();
}

function validateEventInput({ title, description, event_date, capacity }) {
  const errors = [];

  if (typeof title !== 'string' || title.trim().length === 0) {
    errors.push('Title is required.');
  } else if (title.trim().length > 200) {
    errors.push('Title must be 200 characters or fewer.');
  }

  if (description !== undefined && description !== null) {
    if (typeof description !== 'string') {
      errors.push('Description must be text.');
    } else if (description.length > 5000) {
      errors.push('Description must be 5000 characters or fewer.');
    }
  }

  const parsedDate = new Date(event_date);
  if (!event_date || Number.isNaN(parsedDate.getTime())) {
    errors.push('A valid event date/time is required.');
  } else if (parsedDate.getTime() < Date.now()) {
    errors.push('Event date must be in the future.');
  }

  const capacityNum = Number(capacity);
  if (!Number.isInteger(capacityNum) || capacityNum <= 0) {
    errors.push('Capacity must be a positive whole number.');
  }

  return { valid: errors.length === 0, errors, parsedDate, capacityNum };
}

function validateSignupInput({ name, email }) {
  const errors = [];

  if (typeof name !== 'string' || name.trim().length === 0) {
    errors.push('Name is required.');
  } else if (name.trim().length > 200) {
    errors.push('Name must be 200 characters or fewer.');
  }

  if (!isValidEmail(email)) {
    errors.push('A valid email address is required.');
  }

  return { valid: errors.length === 0, errors };
}

module.exports = {
  isValidEmail,
  normalizeEmail,
  validateEventInput,
  validateSignupInput,
};
