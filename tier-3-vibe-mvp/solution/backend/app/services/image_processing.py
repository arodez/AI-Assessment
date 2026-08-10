"""Cover-photo validation + re-encoding, per BRIEF §7.3 (verbatim):

"The uploaded `image` file must be jpeg/png/webp, verified server-side
from the file's actual magic bytes — not just its extension or
client-sent Content-Type header — and rejected otherwise (this also
blocks SVG, which can carry embedded scripts). Minimum 400x250px; maximum
5MB and 4000x4000px. Accepted files are re-encoded and stripped of EXIF
metadata, then saved under a server-generated filename — never the
client-supplied one — to avoid path traversal or filename collisions."
"""

from __future__ import annotations

import io
import uuid
from pathlib import Path

from flask import current_app
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

from app.errors import ValidationEnvelopeError

_EXTENSION_BY_FORMAT = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}


def _error(message: str) -> ValidationEnvelopeError:
    return ValidationEnvelopeError(
        "Request validation failed.", details=[{"field": "image", "message": message}]
    )


def _target_mode(img: Image.Image) -> str:
    """JPEG has no alpha channel — always flatten to RGB for it. PNG/WEBP
    keep an alpha channel if the source actually had one; otherwise RGB.
    """
    if img.format == "JPEG":
        return "RGB"
    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )
    return "RGBA" if has_alpha else "RGB"


def process_cover_image(file_storage: FileStorage | None) -> str | None:
    """Validates + re-encodes an uploaded cover image.

    Returns the relative path to store on Event.image (e.g.
    "events/<uuid>.jpg"), or None if no file was supplied. Raises
    ValidationEnvelopeError (400) on any validation failure — callers
    should validate the image BEFORE writing anything else to the DB, so
    a rejected image never leaves a partially-created Event behind.
    """
    if file_storage is None or file_storage.filename == "":
        return None

    cfg = current_app.config
    raw = file_storage.read()
    if len(raw) > cfg["IMAGE_MAX_BYTES"]:
        raise _error(
            f"Image exceeds the {cfg['IMAGE_MAX_BYTES'] // (1024 * 1024)}MB size limit."
        )

    try:
        probe = Image.open(io.BytesIO(raw))
        probe.verify()  # confirms the stream isn't truncated/corrupt
        img = Image.open(io.BytesIO(raw))  # re-open: verify() invalidates the handle
    except (UnidentifiedImageError, OSError) as exc:
        raise _error("Uploaded file is not a valid image.") from exc

    # Format is read from Pillow's own parse of the file's header bytes —
    # NOT file_storage.filename's extension and NOT file_storage.content_type
    # (both client-controlled and untrusted). This is what satisfies "magic
    # bytes, not extension" — a renamed .svg or a .jpg-named text file is
    # rejected here regardless of what the client claimed it was.
    if img.format not in cfg["IMAGE_ALLOWED_FORMATS"]:
        raise _error("Image must be JPEG, PNG, or WEBP.")
    assert img.format is not None  # narrowed by the check above

    width, height = img.size
    min_w, min_h = cfg["IMAGE_MIN_WIDTH"], cfg["IMAGE_MIN_HEIGHT"]
    if width < min_w or height < min_h:
        raise _error(f"Image must be at least {min_w}x{min_h}px.")
    if width > cfg["IMAGE_MAX_DIM"] or height > cfg["IMAGE_MAX_DIM"]:
        raise _error(
            f"Image must be at most {cfg['IMAGE_MAX_DIM']}x{cfg['IMAGE_MAX_DIM']}px."
        )

    # Re-encode into a fresh image object rather than passing the original
    # bytes through — img.info (EXIF/ICC/etc.) is dropped by convert(),
    # and save() below is never given an exif= kwarg, so no source
    # metadata survives into the saved file.
    clean = img.convert(_target_mode(img))

    ext = _EXTENSION_BY_FORMAT[img.format]
    filename = f"{uuid.uuid4().hex}.{ext}"  # server-generated; never the client's
    upload_dir = Path(cfg["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    clean.save(upload_dir / filename, format=img.format)

    return f"events/{filename}"
