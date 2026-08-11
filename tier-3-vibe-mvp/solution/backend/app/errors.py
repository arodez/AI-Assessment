"""Consistent JSON error envelope for every non-2xx response:

    {"error": "<code>", "message": "...", "details": null | [...]}

`error` is a stable, machine-readable code the frontend can branch on
(e.g. show a specific "this event is full" banner) — BRIEF explicitly
wants "a clear, specific reason (not a generic error)" for a few cases,
and a bare status code can't carry that on its own.

Flask-JWT-Extended's own error callbacks are registered here too (not in
app/extensions.py) so a library-raised 401 (missing/garbled/expired
token) and an app-raised 401 look identical to a client.
"""

from __future__ import annotations

from typing import Any

from flask import Flask, Response, jsonify
from flask.typing import ResponseReturnValue

from app.extensions import jwt


class APIError(Exception):
    """Base class for every error this app raises deliberately (as opposed
    to an unexpected exception, which falls through to the 500 handler).
    """

    status_code = 400
    error_code = "bad_request"

    def __init__(self, message: str, details: list | dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationEnvelopeError(APIError):
    status_code = 400
    error_code = "validation_error"

    @classmethod
    def from_pydantic(cls, exc: Any) -> ValidationEnvelopeError:
        details = [
            {"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return cls("Request validation failed.", details=details)


class UnauthorizedError(APIError):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(APIError):
    """Reserved purely for admin/authorization failures — every
    business-rule/invalid-state rejection uses a 400 subclass instead (see
    EventFullError, AlreadyRegisteredError, NoActiveRegistrationError).
    """

    status_code = 403
    error_code = "forbidden"


class NotFoundError(APIError):
    status_code = 404
    error_code = "not_found"


class EventFullError(APIError):
    status_code = 400
    error_code = "event_full"


class AlreadyRegisteredError(APIError):
    status_code = 400
    error_code = "already_registered"


class NoActiveRegistrationError(APIError):
    status_code = 400
    error_code = "no_active_registration"


def _envelope(
    error: str, message: str, status: int, details: list | dict | None = None
) -> tuple[Response, int]:
    return jsonify(error=error, message=message, details=details), status


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def _handle_api_error(err: APIError) -> ResponseReturnValue:
        return _envelope(err.error_code, err.message, err.status_code, err.details)

    @app.errorhandler(404)
    def _handle_404(err: Any) -> ResponseReturnValue:
        return _envelope("not_found", "Resource not found.", 404)

    @app.errorhandler(405)
    def _handle_405(err: Any) -> ResponseReturnValue:
        return _envelope(
            "method_not_allowed", "Method not allowed for this route.", 405
        )

    @app.errorhandler(413)
    def _handle_413(err: Any) -> ResponseReturnValue:
        return _envelope(
            "payload_too_large", "Request body exceeds the maximum allowed size.", 413
        )

    @app.errorhandler(500)
    def _handle_500(err: Any) -> ResponseReturnValue:
        return _envelope("internal_error", "Unexpected server error.", 500)

    # Flask-JWT-Extended callbacks. Registered here (not app/extensions.py)
    # so they share the same _envelope() helper as everything else.
    @jwt.unauthorized_loader
    def _missing_token(reason: str) -> ResponseReturnValue:
        return _envelope("missing_token", "Authorization token is required.", 401)

    @jwt.invalid_token_loader
    def _invalid_token(reason: str) -> ResponseReturnValue:
        return _envelope("invalid_token", "Authorization token is invalid.", 401)

    @jwt.expired_token_loader
    def _expired_token(header: dict, payload: dict) -> ResponseReturnValue:
        return _envelope("token_expired", "Authorization token has expired.", 401)
