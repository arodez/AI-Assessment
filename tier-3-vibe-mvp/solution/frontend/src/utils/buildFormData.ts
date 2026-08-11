import type { CreateEventFormValues } from '../schemas/createEventSchema';

/** Shared by buildEventFormData and the live preview so the "what does
 * `location` actually contain" logic can't drift between the two. */
export function buildLocationArray(values: CreateEventFormValues): string[] {
  const location = values.location.trim();
  const virtualLink = values.virtualLink.trim();

  if (values.locationType === 'virtual') {
    return virtualLink ? [virtualLink] : [];
  }
  if (values.locationType === 'hybrid') {
    return [location, virtualLink].filter(Boolean);
  }
  return location ? [location] : [];
}

/** Maps validated form values (+ the separately-managed cover photo File)
 * to the multipart body the backend expects. `start`/`end` combine
 * date+time into `${date}T${time}:00` with no timezone suffix —
 * deliberately not `Date.toISOString()`, matching the backend's naive-
 * datetime storage. `location` is JSON-encoded into a single form field
 * per the API's documented convention (multipart has no native array
 * type). Blank optional fields are omitted rather than sent as "". */
export function buildEventFormData(
  values: CreateEventFormValues,
  coverPhoto: File | null,
): FormData {
  const formData = new FormData();
  formData.append('title', values.title.trim());
  formData.append('start', `${values.date}T${values.startTime}:00`);
  formData.append('end', `${values.date}T${values.endTime}:00`);
  formData.append('spots', String(values.spots));
  formData.append('event_type', values.eventType);
  formData.append('location_type', values.locationType);

  const description = values.description.trim();
  if (description) formData.append('description', description);

  const hostName = values.hostName.trim();
  if (hostName) formData.append('host_name', hostName);

  const hostTeam = values.hostTeam.trim();
  if (hostTeam) formData.append('host_team', hostTeam);

  const location = buildLocationArray(values);
  if (location.length > 0) formData.append('location', JSON.stringify(location));

  if (coverPhoto) formData.append('image', coverPhoto);

  return formData;
}
