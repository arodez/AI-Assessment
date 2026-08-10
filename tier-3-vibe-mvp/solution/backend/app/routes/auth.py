"""POST /login — BRIEF §7.1.

Company-email-only auth, no password. Because account creation is out of
scope for this MVP, this NEVER creates a User row — login only succeeds
for an email matching one of the seeded fixture users (case-insensitive).
"""

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import create_access_token
from pydantic import ValidationError

from app.errors import UnauthorizedError, ValidationEnvelopeError
from app.models import User
from app.schemas.auth import LoginRequest

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login() -> ResponseReturnValue:
    try:
        payload = LoginRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as exc:
        raise ValidationEnvelopeError.from_pydantic(exc) from exc

    user = User.query.filter(User.email.ilike(payload.email)).first()
    if user is None:
        raise UnauthorizedError("Email not recognized.")

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"email": user.email, "is_admin": user.is_admin},
    )

    return (
        jsonify(
            access_token=token,
            user={
                "id": user.id,
                "first_name": user.first_name,
                "is_admin": user.is_admin,
            },
        ),
        200,
    )
