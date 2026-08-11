import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

// jsdom doesn't implement these — several components (CoverPhotoUpload,
// CreateEventForm's preview pane, OrganizerViewPage's CSV export) call
// them for local file/blob previews and downloads.
URL.createObjectURL = vi.fn(() => 'blob:mock-url');
URL.revokeObjectURL = vi.fn();
