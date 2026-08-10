"""Auth helpers built on Flask-JWT-Extended.

BRIEF §7.1: POST /login issues a JWT carrying `sub` (user id), `email`,
`is_admin`, with a fixed expiry and no refresh/logout flow. Everything
here is just verifying that token and exposing its claims — the token is
issued in app/routes/auth.py.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.errors import ForbiddenError


def admin_required(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Verifies the JWT AND the is_admin claim before the wrapped view
    body ever runs.

    This ordering is load-bearing, not stylistic: BRIEF requires that a
    non-admin hitting an organizer-only endpoint gets 403 even for a
    nonexistent resource id (the response must not leak whether the
    resource exists). Because this decorator wraps the entire view
    function, the 403 below always fires before a single line of the
    route body — including any event-id lookup — runs.
    """

    @wraps(fn)
    @jwt_required()
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not get_jwt().get("is_admin", False):
            raise ForbiddenError("Admin privileges required.")
        return fn(*args, **kwargs)

    return wrapper


def current_user_id() -> int:
    """The calling user's id, from the JWT's `sub` claim.

    Flask-JWT-Extended requires `identity` to be a plain string when the
    token is created (see app/routes/auth.py) — cast back to int here so
    callers don't have to think about it.
    """
    return int(get_jwt_identity())


def current_user_is_admin() -> bool:
    return bool(get_jwt().get("is_admin", False))
