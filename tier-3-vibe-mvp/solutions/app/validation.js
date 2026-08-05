'use strict';

// Deliberately conservative email regex — good enough to reject obviously
// malformed input without trying to be a full RFC 5322 validator (which is
// notoriously hard to get right and not worth it for an MVP).
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const MAX_TITLE_LEN = 200;
const MAX_DESCRIPTION_LEN = 2000;
const MAX_NAME_LEN = 200;

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Validates event creation input.
 * Returns { valid: true, data } or { valid: false, errors: string[] }
 */
function validateEventInput({ title, eventDate, description, capacity }) {
  const errors = [];

  const cleanTitle = typeof title === 'string' ? title.trim() : '';
  if (!cleanTitle) {
    errors.push('Title is required.');
  } else if (cleanTitle.length > MAX_TITLE_LEN) {
    errors.push(`Title must be ${MAX_TITLE_LEN} characters or fewer.`);
  }

  const cleanDate = typeof eventDate === 'string' ? eventDate.trim() : '';
  const dateObj = new Date(cleanDate);
  if (!cleanDate || Number.isNaN(dateObj.getTime())) {
    errors.push('A valid date is required.');
  } else if (cleanDate < todayIso()) {
    errors.push('Event date must be today or in the future.');
  }

  const cleanDescription =
    typeof description === 'string' ? description.trim() : '';
  if (cleanDescription.length > MAX_DESCRIPTION_LEN) {
    errors.push(`Description must be ${MAX_DESCRIPTION_LEN} characters or fewer.`);
  }

  // Capacity: must be a positive integer. Reject decimals, negatives, zero,
  // non-numeric strings, and anything that doesn't round-trip cleanly.
  let cleanCapacity = null;
  if (capacity === '' || capacity === null || capacity === undefined) {
    errors.push('Capacity is required.');
  } else {
    const asNumber = Number(capacity);
    if (
      !Number.isFinite(asNumber) ||
      !Number.isInteger(asNumber) ||
      asNumber <= 0 ||
      String(capacity).trim() !== String(asNumber)
    ) {
      errors.push('Capacity must be a positive whole number.');
    } else {
      cleanCapacity = asNumber;
    }
  }

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  return {
    valid: true,
    data: {
      title: cleanTitle,
      eventDate: cleanDate,
      description: cleanDescription,
      capacity: cleanCapacity,
    },
  };
}

/**
 * Validates RSVP (sign-up) input.
 * Returns { valid: true, data } or { valid: false, errors: string[] }
 */
function validateRsvpInput({ name, email }) {
  const errors = [];

  const cleanName = typeof name === 'string' ? name.trim() : '';
  if (!cleanName) {
    errors.push('Name is required.');
  } else if (cleanName.length > MAX_NAME_LEN) {
    errors.push(`Name must be ${MAX_NAME_LEN} characters or fewer.`);
  }

  const cleanEmail = typeof email === 'string' ? email.trim() : '';
  if (!cleanEmail) {
    errors.push('Email is required.');
  } else if (!EMAIL_RE.test(cleanEmail)) {
    errors.push('Email format is invalid.');
  }

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  return { valid: true, data: { name: cleanName, email: cleanEmail } };
}

module.exports = { validateEventInput, validateRsvpInput };
