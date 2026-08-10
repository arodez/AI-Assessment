from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def reject_surrounding_whitespace(cls, v: object) -> object:
        # BRIEF explicitly lists "trailing whitespace" as an example of
        # malformed input that must be rejected outright — not silently
        # trimmed and accepted. This runs before EmailStr's own coercion,
        # so " alice.kim@company.com" / "alice.kim@company.com " fail
        # deterministically regardless of the installed email-validator
        # version's own whitespace handling.
        if not isinstance(v, str) or v != v.strip() or v.strip() == "":
            raise ValueError(
                "email must not be empty or contain surrounding whitespace"
            )
        return v
