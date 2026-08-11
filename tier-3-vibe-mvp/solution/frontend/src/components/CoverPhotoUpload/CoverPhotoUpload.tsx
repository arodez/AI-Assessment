import {
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type KeyboardEvent,
} from 'react';
import styles from './CoverPhotoUpload.module.css';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_BYTES = 5 * 1024 * 1024;

interface CoverPhotoUploadProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
}

/** Drag-and-drop + click-to-browse + object-URL preview + Remove.
 *
 * The mockup's `image-slot.js` also supports drag-to-reposition/pinch-
 * zoom crop framing — that's prototyping tooling with no backing field
 * in the real API (no crop-offset column exists anywhere), so it's
 * deliberately not reproduced here. Dimension/re-encode validation stays
 * server-only (Pillow does the real check); this component only
 * pre-checks mime type and file size for fast feedback. */
export function CoverPhotoUpload({ file, onFileChange }: CoverPhotoUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function validateAndSet(candidate: File | undefined | null) {
    if (!candidate) return;
    if (!ACCEPTED_TYPES.includes(candidate.type)) {
      setError('Please choose a JPEG, PNG, or WebP image.');
      return;
    }
    if (candidate.size > MAX_BYTES) {
      setError('Image must be 5MB or smaller.');
      return;
    }
    setError(null);
    onFileChange(candidate);
  }

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    validateAndSet(event.target.files?.[0]);
    event.target.value = '';
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragOver(false);
    validateAndSet(event.dataTransfer.files[0]);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      inputRef.current?.click();
    }
  }

  function handleRemove() {
    setError(null);
    onFileChange(null);
  }

  return (
    <div>
      <div
        className={`${styles.dropzone} ${isDragOver ? styles.dragOver : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onKeyDown={handleKeyDown}
      >
        {previewUrl ? (
          <img src={previewUrl} alt="Cover preview" className={styles.preview} />
        ) : (
          <span className={styles.placeholder}>Drop a cover photo</span>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleInputChange}
          className={styles.hiddenInput}
          aria-label="Cover photo"
        />
      </div>
      {previewUrl && (
        <button type="button" className={styles.removeButton} onClick={handleRemove}>
          Remove
        </button>
      )}
      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
}
