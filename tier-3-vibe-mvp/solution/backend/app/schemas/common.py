"""Small validators shared across more than one Pydantic schema."""

import re

_URL_RE = re.compile(r"^https?://[^\s]+\.[^\s]+", re.IGNORECASE)


def is_probable_url(value: str) -> bool:
    """A deliberately loose check — BRIEF just wants "a well-formed URL
    (e.g. a Zoom, Google Meet, or YouTube link)", not a full RFC 3986
    parser. http(s):// followed by something dot-something is enough to
    catch a plain room name (BRIEF's actual failure case) while accepting
    any real meeting-link provider without a maintained allowlist.
    """
    return bool(_URL_RE.match(value.strip()))


def blank_to_none(value: object) -> object:
    """Normalizes an HTML/JS form's "field left blank" (`field=""`) to
    None, matching "field omitted" — otherwise an optional str field would
    accept "" as a valid non-null value, which nothing downstream expects.
    """
    if isinstance(value, str) and value.strip() == "":
        return None
    return value
