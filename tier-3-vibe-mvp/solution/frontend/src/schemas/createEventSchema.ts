import { z } from 'zod';

const EVENT_TYPES = ['study_group', 'ama', 'workshop', 'social', 'other'] as const;
const LOCATION_TYPES = ['in_person', 'hybrid', 'virtual'] as const;

function isHttpUrl(value: string): boolean {
  if (!value) return false;
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

/**
 * Mirrors every backend rule from docs/API.md's `POST /event` table so a
 * bad submission is caught client-side before it ever hits the network:
 * title length, positive integer spots, end-after-start, and a
 * hybrid/virtual location requiring an http(s) link. The cover photo is
 * validated separately in CoverPhotoUpload (mime type, size) —
 * dimension/re-encode checks stay server-only (Pillow is the authority).
 */
export const createEventSchema = z
  .object({
    title: z
      .string()
      .trim()
      .min(3, 'Title must be at least 3 characters.')
      .max(140, 'Title must be 140 characters or fewer.'),
    description: z.string().trim().max(2000, 'Description must be 2000 characters or fewer.'),
    eventType: z.enum(EVENT_TYPES),
    locationType: z.enum(LOCATION_TYPES),
    location: z.string().trim().max(200, 'Keep it under 200 characters.'),
    virtualLink: z.string().trim().max(300, 'Keep it under 300 characters.'),
    date: z.string().min(1, 'Pick a date.'),
    startTime: z.string().min(1, 'Pick a start time.'),
    endTime: z.string().min(1, 'Pick an end time.'),
    hostName: z.string().trim().max(100, 'Keep it under 100 characters.'),
    hostTeam: z.string().trim().max(100, 'Keep it under 100 characters.'),
    spots: z
      .number()
      .refine((n) => Number.isFinite(n), 'Enter the number of spots.')
      .int('Spots must be a whole number.')
      .positive('Spots must be at least 1.'),
  })
  .superRefine((data, ctx) => {
    if (data.date && data.startTime && data.endTime) {
      const start = new Date(`${data.date}T${data.startTime}:00`);
      const end = new Date(`${data.date}T${data.endTime}:00`);
      if (end.getTime() <= start.getTime()) {
        ctx.addIssue({
          code: 'custom',
          message: 'End time must be after start time.',
          path: ['endTime'],
        });
      }
    }

    if (data.locationType === 'in_person' && !data.location) {
      ctx.addIssue({ code: 'custom', message: 'Add a room or building.', path: ['location'] });
    }

    if (data.locationType === 'virtual' && !isHttpUrl(data.virtualLink)) {
      ctx.addIssue({
        code: 'custom',
        message: 'Enter a valid http(s) link.',
        path: ['virtualLink'],
      });
    }

    if (data.locationType === 'hybrid') {
      if (!data.location) {
        ctx.addIssue({ code: 'custom', message: 'Add a room or building.', path: ['location'] });
      }
      if (!isHttpUrl(data.virtualLink)) {
        ctx.addIssue({
          code: 'custom',
          message: 'Enter a valid http(s) link.',
          path: ['virtualLink'],
        });
      }
    }
  });

export type CreateEventFormValues = z.infer<typeof createEventSchema>;

export const DEFAULT_CREATE_EVENT_VALUES: CreateEventFormValues = {
  title: '',
  description: '',
  eventType: 'workshop',
  locationType: 'in_person',
  location: '',
  virtualLink: '',
  date: '',
  startTime: '',
  endTime: '',
  hostName: '',
  hostTeam: '',
  spots: 20,
};
