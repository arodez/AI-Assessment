import type { EventDTO } from '../api/types';

export function makeEvent(overrides: Partial<EventDTO> = {}): EventDTO {
  return {
    id: 1,
    title: 'Test Event',
    start: '2026-08-10T10:00:00',
    end: '2026-08-10T11:00:00',
    spots: 10,
    remaining_spots: 5,
    event_type: 'workshop',
    location_type: 'in_person',
    description: 'A test event.',
    image_url: null,
    location: ['Room 1'],
    host_name: 'Host Person',
    host_team: 'Test Team',
    viewer_status: null,
    created_at: '2026-08-01T00:00:00',
    updated_at: '2026-08-01T00:00:00',
    ...overrides,
  };
}
