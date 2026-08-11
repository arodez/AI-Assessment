"""EventCreateRequest — validates POST /event's multipart form fields
against every rule in BRIEF §7.3.

Multipart form fields all arrive as strings. Pydantic v2 coerces
"3" -> int 3 (rejecting "3.5"/"abc"), and parses ISO-8601 datetime
strings natively, so `spots: int` / `start: datetime` need no extra code
to satisfy BRIEF's "non-integer capacity" / malformed-date edge cases.

`location` (array(text) in BRIEF) has no native representation in
multipart/form-data. Concrete choice: the client sends a single
JSON-encoded string field, e.g.
`formData.append("location", JSON.stringify(["Room 12", "https://..."]))`.
`Json[list[str]]` parses that string as JSON and validates the result
against `list[str]` in one step — no manual `json.loads` in the route.
"""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, Json, field_validator, model_validator

from app.models.enums import EventType, LocationType
from app.schemas.common import blank_to_none, is_probable_url


class EventCreateRequest(BaseModel):
    title: str
    start: datetime
    end: datetime
    spots: int
    event_type: EventType
    location_type: LocationType
    description: str | None = Field(default=None, max_length=2000)
    location: Json[list[str]] | None = None
    host_name: str | None = Field(default=None, max_length=100)
    host_team: str | None = Field(default=None, max_length=100)

    @field_validator("description", "host_name", "host_team", mode="before")
    @classmethod
    def _blank_to_none(cls, v: object) -> object:
        return blank_to_none(v)

    @field_validator("title")
    @classmethod
    def title_bounds(cls, v: str) -> str:
        stripped = v.strip()
        if not (3 <= len(stripped) <= 140):
            raise ValueError(
                "title must be 3-140 characters (after trimming whitespace)"
            )
        return stripped

    @field_validator("spots")
    @classmethod
    def spots_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("spots must be a positive integer")
        return v

    @field_validator("location")
    @classmethod
    def location_bounds(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        if len(v) > 5:
            raise ValueError("location may have at most 5 entries")
        if any(len(entry) > 200 for entry in v):
            raise ValueError("each location entry must be at most 200 characters")
        return v

    @model_validator(mode="after")
    def end_after_start(self) -> Self:
        if self.end <= self.start:
            raise ValueError("end must be strictly after start")
        return self

    @model_validator(mode="after")
    def virtual_hybrid_requires_url(self) -> Self:
        if self.location_type in (LocationType.VIRTUAL, LocationType.HYBRID):
            entries = self.location or []
            if not any(is_probable_url(e) for e in entries):
                raise ValueError(
                    "virtual/hybrid events require at least one "
                    "well-formed URL in location"
                )
        return self
