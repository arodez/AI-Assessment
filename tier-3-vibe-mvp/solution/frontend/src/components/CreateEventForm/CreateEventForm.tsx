import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { ApiError } from '../../api/client';
import type { EventDTO } from '../../api/types';
import { useCreateEventMutation } from '../../hooks/useCreateEventMutation';
import {
  createEventSchema,
  DEFAULT_CREATE_EVENT_VALUES,
  type CreateEventFormValues,
} from '../../schemas/createEventSchema';
import { buildEventFormData, buildLocationArray } from '../../utils/buildFormData';
import { CategoryTypeSelector } from '../CategoryTypeSelector/CategoryTypeSelector';
import { CoverPhotoUpload } from '../CoverPhotoUpload/CoverPhotoUpload';
import { EventCard } from '../EventCard/EventCard';
import { LocationTypeToggle } from '../LocationTypeToggle/LocationTypeToggle';
import styles from './CreateEventForm.module.css';

/** Builds a fake-but-EventDTO-shaped object from the in-progress form
 * values so the preview pane can render the exact same EventCard the
 * feed uses, rather than a second hand-rolled layout that could drift
 * out of sync. Blank date/time fields fall back to "now" so the date
 * formatter always has something parseable — this trades the mockup's
 * literal "SELECT A DATE" placeholder text for simpler, safer reuse. */
function buildPreviewEvent(values: CreateEventFormValues, coverImageUrl: string | null): EventDTO {
  const now = new Date().toISOString();
  const hasStart = values.date && values.startTime;
  const hasEnd = values.date && values.endTime;
  const spots = Number.isFinite(values.spots) && values.spots > 0 ? values.spots : 0;

  return {
    id: -1,
    title: values.title.trim() || 'Your event title',
    start: hasStart ? `${values.date}T${values.startTime}:00` : now,
    end: hasEnd ? `${values.date}T${values.endTime}:00` : now,
    spots,
    remaining_spots: spots,
    event_type: values.eventType,
    location_type: values.locationType,
    description: values.description.trim() || null,
    image_url: coverImageUrl,
    location: buildLocationArray(values),
    host_name: values.hostName.trim() || 'You',
    host_team: values.hostTeam.trim() || 'Your team',
    viewer_status: null,
    created_at: now,
    updated_at: now,
  };
}

export function CreateEventForm() {
  const navigate = useNavigate();
  const [coverPhoto, setCoverPhoto] = useState<File | null>(null);
  const [coverImageUrl, setCoverImageUrl] = useState<string | null>(null);
  const createEventMutation = useCreateEventMutation();

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CreateEventFormValues>({
    resolver: zodResolver(createEventSchema),
    defaultValues: DEFAULT_CREATE_EVENT_VALUES,
  });

  // Owned here (not inside CoverPhotoUpload) because the preview pane
  // needs the same object URL — a second independent one would work but
  // means two blob URLs alive for one file at a time.
  useEffect(() => {
    if (!coverPhoto) {
      setCoverImageUrl(null);
      return;
    }
    const url = URL.createObjectURL(coverPhoto);
    setCoverImageUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [coverPhoto]);

  const values = watch();
  const submitError =
    createEventMutation.error instanceof ApiError ? createEventMutation.error.message : null;

  async function onSubmit(formValues: CreateEventFormValues) {
    const formData = buildEventFormData(formValues, coverPhoto);
    await createEventMutation.mutateAsync(formData);
    navigate('/events');
  }

  const previewEvent = buildPreviewEvent(values, coverImageUrl);

  return (
    <div className={styles.layout}>
      <form
        className={styles.form}
        onSubmit={(event) => void handleSubmit(onSubmit)(event)}
        noValidate
      >
        <div>
          <label className={styles.label}>Cover Photo</label>
          <CoverPhotoUpload file={coverPhoto} onFileChange={setCoverPhoto} />
        </div>

        <div>
          <label className={styles.label}>Event Type</label>
          <Controller
            control={control}
            name="eventType"
            render={({ field }) => (
              <CategoryTypeSelector value={field.value} onChange={field.onChange} />
            )}
          />
        </div>

        <div>
          <label className={styles.label} htmlFor="title">
            Title
          </label>
          <input
            id="title"
            type="text"
            className={styles.input}
            placeholder="e.g. Figma Variables Workshop"
            {...register('title')}
          />
          {errors.title && <p className={styles.fieldError}>{errors.title.message}</p>}
        </div>

        <div>
          <label className={styles.label} htmlFor="description">
            Description
          </label>
          <textarea
            id="description"
            rows={4}
            className={styles.textarea}
            placeholder="What will people learn or do? Anything they should bring or prep?"
            {...register('description')}
          />
          {errors.description && <p className={styles.fieldError}>{errors.description.message}</p>}
        </div>

        <div>
          <label className={styles.label}>Date &amp; Time</label>
          <div className={styles.row}>
            <input type="date" className={styles.input} {...register('date')} />
            <input type="time" className={styles.input} {...register('startTime')} />
            <input type="time" className={styles.input} {...register('endTime')} />
          </div>
          {(errors.date ?? errors.startTime ?? errors.endTime) && (
            <p className={styles.fieldError}>
              {errors.date?.message ?? errors.startTime?.message ?? errors.endTime?.message}
            </p>
          )}
        </div>

        <div>
          <label className={styles.label}>Location</label>
          <Controller
            control={control}
            name="locationType"
            render={({ field }) => (
              <LocationTypeToggle value={field.value} onChange={field.onChange} />
            )}
          />
          {(values.locationType === 'in_person' || values.locationType === 'hybrid') && (
            <input
              type="text"
              className={styles.input}
              placeholder="e.g. Room 12, Rooftop Terrace"
              style={{ marginBottom: values.locationType === 'hybrid' ? 10 : 0 }}
              {...register('location')}
            />
          )}
          {(values.locationType === 'virtual' || values.locationType === 'hybrid') && (
            <input
              type="text"
              className={styles.input}
              placeholder="e.g. Zoom, Google Meet link"
              {...register('virtualLink')}
            />
          )}
          {(errors.location ?? errors.virtualLink) && (
            <p className={styles.fieldError}>
              {errors.location?.message ?? errors.virtualLink?.message}
            </p>
          )}
        </div>

        <div className={styles.row}>
          <div className={styles.grow}>
            <label className={styles.label} htmlFor="hostName">
              Host Name
            </label>
            <input
              id="hostName"
              type="text"
              className={styles.input}
              placeholder="Your name"
              {...register('hostName')}
            />
            {errors.hostName && <p className={styles.fieldError}>{errors.hostName.message}</p>}
          </div>
          <div className={styles.grow}>
            <label className={styles.label} htmlFor="hostTeam">
              Host Team
            </label>
            <input
              id="hostTeam"
              type="text"
              className={styles.input}
              placeholder="e.g. Design Systems"
              {...register('hostTeam')}
            />
            {errors.hostTeam && <p className={styles.fieldError}>{errors.hostTeam.message}</p>}
          </div>
        </div>

        <div>
          <label className={styles.label} htmlFor="spots">
            Spots Available
          </label>
          <input
            id="spots"
            type="number"
            min={1}
            className={styles.spotsInput}
            {...register('spots', { valueAsNumber: true })}
          />
          {errors.spots && <p className={styles.fieldError}>{errors.spots.message}</p>}
        </div>

        {submitError && <p className={styles.fieldError}>{submitError}</p>}

        <div>
          <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
            {isSubmitting ? 'Publishing…' : 'Publish event'}
          </button>
        </div>
      </form>

      <aside className={styles.previewPane}>
        <div className={styles.previewLabel}>Preview · how attendees will see it</div>
        {/* Preview is decorative only: pointer-events are disabled so a
            stray click can't open the detail modal or fire a real
            register/cancel mutation against this placeholder event id. */}
        <div className={styles.previewInert}>
          <EventCard event={previewEvent} onClick={() => {}} />
        </div>
      </aside>
    </div>
  );
}
