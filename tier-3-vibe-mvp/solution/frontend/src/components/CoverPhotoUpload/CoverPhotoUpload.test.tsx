import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CoverPhotoUpload } from './CoverPhotoUpload';

function makeFile(name: string, type: string, sizeBytes = 1024): File {
  return new File([new Uint8Array(sizeBytes)], name, { type });
}

describe('CoverPhotoUpload', () => {
  it('accepts a valid dropped image and calls onFileChange with it', () => {
    const onFileChange = vi.fn();
    render(<CoverPhotoUpload file={null} onFileChange={onFileChange} />);

    const file = makeFile('cover.jpg', 'image/jpeg');
    fireEvent.drop(screen.getByRole('button'), { dataTransfer: { files: [file] } });

    expect(onFileChange).toHaveBeenCalledWith(file);
  });

  it('rejects a non-image file with an inline error and does not call onFileChange', () => {
    const onFileChange = vi.fn();
    render(<CoverPhotoUpload file={null} onFileChange={onFileChange} />);

    const file = makeFile('notes.pdf', 'application/pdf');
    fireEvent.drop(screen.getByRole('button'), { dataTransfer: { files: [file] } });

    expect(onFileChange).not.toHaveBeenCalled();
    expect(screen.getByText('Please choose a JPEG, PNG, or WebP image.')).toBeInTheDocument();
  });

  it('rejects a file over 5MB', () => {
    const onFileChange = vi.fn();
    render(<CoverPhotoUpload file={null} onFileChange={onFileChange} />);

    const file = makeFile('huge.jpg', 'image/jpeg', 6 * 1024 * 1024);
    fireEvent.drop(screen.getByRole('button'), { dataTransfer: { files: [file] } });

    expect(onFileChange).not.toHaveBeenCalled();
    expect(screen.getByText('Image must be 5MB or smaller.')).toBeInTheDocument();
  });

  it('shows a Remove button once a file is selected, and clicking it clears the file', () => {
    const file = makeFile('cover.jpg', 'image/jpeg');
    const onFileChange = vi.fn();
    render(<CoverPhotoUpload file={file} onFileChange={onFileChange} />);

    fireEvent.click(screen.getByRole('button', { name: 'Remove' }));

    expect(onFileChange).toHaveBeenCalledWith(null);
  });

  it('renders no Remove button and a placeholder when no file is selected', () => {
    render(<CoverPhotoUpload file={null} onFileChange={vi.fn()} />);

    expect(screen.getByText('Drop a cover photo')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Remove' })).not.toBeInTheDocument();
  });
});
